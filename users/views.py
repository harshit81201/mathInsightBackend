from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from django.db.models import Avg, Count, Sum, Q, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserSerializer, LoginSerializer, TeacherRegisterSerializer,
    AllChildrenPerformanceSerializer, ChildDetailedPerformanceSerializer,
    ChildPerformanceSummarySerializer, QuizAttemptPerformanceSerializer,
    PerformanceTrendDataSerializer
)
from students.models import Student
from quizzes.models import QuizAttempt, Quiz


class TeacherRegisterView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = TeacherRegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		from rest_framework_simplejwt.tokens import RefreshToken
		refresh = RefreshToken.for_user(user)
		return Response({
			"token": str(refresh.access_token),
			"user": UserSerializer(user).data
		}, status=201)


class LoginView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		email = serializer.validated_data["email"]
		password = serializer.validated_data["password"]
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
		user = authenticate(request, username=user.username, password=password)
		if not user:
			return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
		refresh = RefreshToken.for_user(user)
		token_str = str(refresh.access_token)
		print(f"LOGIN SUCCESS: {user.email}, Token: {token_str}")
		return Response({
			"token": token_str,
			"user": UserSerializer(user).data
		})

class MeView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		return Response(UserSerializer(request.user).data)

class TeacherProfileView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, pk):
		try:
			teacher = User.objects.get(pk=pk, role="teacher")
		except User.DoesNotExist:
			return Response({"error": "Teacher not found"}, status=404)
		return Response(UserSerializer(teacher).data)

class TeacherStudentsView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, pk):
		from students.models import Student
		from students.serializers import StudentSerializer
		students = Student.objects.filter(teacher_id=pk)
		return Response(StudentSerializer(students, many=True).data)

class ParentProfileView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)
		from students.models import Student
		children = Student.objects.filter(parent=request.user)
		data = UserSerializer(request.user).data
		data["children"] = [
			{"id": c.id, "name": c.name, "class_name": c.class_name} for c in children
		]
		return Response(data)

class ParentChildrenView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)
		from students.models import Student
		children = Student.objects.filter(parent=request.user)
		return Response([{"id": c.id, "name": c.name, "class_name": c.class_name} for c in children])


# Parent Performance Views

class ParentAllChildrenPerformanceView(APIView):
	"""
	GET /api/parent/performance/ - Get performance overview for all children
	"""
	permission_classes = [IsAuthenticated]

	def get(self, request):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)

		parent = request.user
		children = Student.objects.filter(parent=parent).select_related('teacher')

		if not children.exists():
			return Response({
				"children_count": 0,
				"overall_statistics": {},
				"children_performance": []
			})

		children_performance = []
		total_attempts = 0
		total_score = 0
		total_possible = 0

		for child in children:
			attempts = QuizAttempt.objects.filter(student=child).select_related('quiz')

			if attempts.exists():
				completed_attempts = attempts.filter(is_completed=True)

				# Calculate basic statistics
				completed_count = completed_attempts.count()
				if completed_count > 0:
					# Calculate averages and totals separately
					total_score_child = sum(attempt.score for attempt in completed_attempts)
					total_possible_child = sum(attempt.total_marks for attempt in completed_attempts)
					avg_percentage = (total_score_child / total_possible_child * 100) if total_possible_child > 0 else 0

					# Get min/max scores for percentage calculation
					max_attempt = completed_attempts.order_by('-score').first()
					min_attempt = completed_attempts.order_by('score').first()
					max_percentage = (max_attempt.score / max_attempt.total_marks * 100) if max_attempt and max_attempt.total_marks > 0 else 0
					min_percentage = (min_attempt.score / min_attempt.total_marks * 100) if min_attempt and min_attempt.total_marks > 0 else 0
				else:
					total_score_child = 0
					total_possible_child = 0
					avg_percentage = 0
					max_percentage = 0
					min_percentage = 0

				# Calculate trend (compare last 3 vs previous 3 attempts)
				recent_attempts = list(completed_attempts.order_by('-attempted_at')[:6])
				trend = self._calculate_trend(recent_attempts)

				# Performance level
				performance_level = self._get_performance_level(avg_percentage)

				children_performance.append({
					"student_id": child.id,
					"student_name": child.name,
					"class_name": child.class_name,
					"teacher_name": child.teacher.get_full_name() or child.teacher.username,
					"total_quizzes_attempted": attempts.count(),
					"completed_quizzes": completed_count,
					"incomplete_quizzes": attempts.filter(is_completed=False).count(),
					"average_score_percentage": round(avg_percentage, 2),
					"highest_score_percentage": round(max_percentage, 2),
					"lowest_score_percentage": round(min_percentage, 2),
					"total_marks_earned": total_score_child,
					"total_possible_marks": total_possible_child,
					"recent_performance_trend": trend,
					"last_quiz_date": attempts.order_by('-attempted_at').first().attempted_at if attempts.exists() else None,
					"performance_level": performance_level
				})

				total_attempts += completed_count
				total_score += total_score_child
				total_possible += total_possible_child		# Overall statistics
		overall_stats = {
			"total_children": children.count(),
			"total_quiz_attempts": total_attempts,
			"overall_average_percentage": round((total_score / max(total_possible, 1)) * 100, 2),
			"total_marks_earned": total_score,
			"total_possible_marks": total_possible
		}

		return Response({
			"children_count": children.count(),
			"overall_statistics": overall_stats,
			"children_performance": children_performance
		})

	def _calculate_trend(self, attempts):
		"""Calculate performance trend based on recent attempts"""
		if len(attempts) < 3:
			return "insufficient_data"

		# Split into recent vs older attempts
		recent = attempts[:3]
		older = attempts[3:6] if len(attempts) >= 6 else attempts[3:]

		if not older:
			return "insufficient_data"

		recent_avg = sum(a.percentage for a in recent) / len(recent)
		older_avg = sum(a.percentage for a in older) / len(older)

		diff = recent_avg - older_avg

		if diff > 5:
			return "improving"
		elif diff < -5:
			return "declining"
		else:
			return "stable"

	def _get_performance_level(self, percentage):
		"""Get performance level based on percentage"""
		if percentage >= 90:
			return "Excellent"
		elif percentage >= 80:
			return "Very Good"
		elif percentage >= 70:
			return "Good"
		elif percentage >= 60:
			return "Fair"
		else:
			return "Needs Improvement"


class ParentChildPerformanceDetailView(APIView):
	"""
	GET /api/parent/performance/child/{child_id}/ - Get detailed performance for specific child
	"""
	permission_classes = [IsAuthenticated]

	def get(self, request, child_id):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)

		try:
			child = Student.objects.select_related('teacher').get(
				id=child_id,
				parent=request.user
			)
		except Student.DoesNotExist:
			return Response({"error": "Child not found"}, status=404)

		# Get all quiz attempts for this child
		attempts = QuizAttempt.objects.filter(student=child).select_related('quiz').order_by('-attempted_at')

		# Performance summary
		performance_summary = self._get_child_performance_summary(child, attempts)

		# Detailed quiz attempts
		quiz_attempts = []
		for attempt in attempts:
			quiz_attempts.append(QuizAttemptPerformanceSerializer(attempt).data)

		# Performance trends (monthly)
		performance_trends = self._get_performance_trends(attempts)

		return Response({
			"student_id": child.id,
			"student_name": child.name,
			"class_name": child.class_name,
			"teacher_name": child.teacher.get_full_name() or child.teacher.username,
			"performance_summary": performance_summary,
			"quiz_attempts": quiz_attempts,
			"performance_trends": performance_trends
		})

	def _get_child_performance_summary(self, child, attempts):
		"""Get performance summary for a child"""
		if not attempts.exists():
			return {
				"student_id": child.id,
				"student_name": child.name,
				"class_name": child.class_name,
				"teacher_name": child.teacher.get_full_name() or child.teacher.username,
				"total_quizzes_attempted": 0,
				"completed_quizzes": 0,
				"incomplete_quizzes": 0,
				"average_score_percentage": 0,
				"highest_score_percentage": 0,
				"lowest_score_percentage": 0,
				"total_marks_earned": 0,
				"total_possible_marks": 0,
				"recent_performance_trend": "no_data",
				"last_quiz_date": None,
				"performance_level": "No Data"
			}

		completed_attempts = attempts.filter(is_completed=True)

		if completed_attempts.exists():
			# Calculate averages and statistics
			percentages = [attempt.percentage for attempt in completed_attempts]
			avg_percentage = sum(percentages) / len(percentages)

			# Calculate totals without aggregation conflicts
			total_marks_earned = sum(attempt.score for attempt in completed_attempts)
			total_possible_marks = sum(attempt.total_marks for attempt in completed_attempts)
		else:
			avg_percentage = 0
			percentages = []
			total_marks_earned = 0
			total_possible_marks = 0

		# Calculate trend
		trend = self._calculate_trend(list(completed_attempts[:6]))

		return {
			"student_id": child.id,
			"student_name": child.name,
			"class_name": child.class_name,
			"teacher_name": child.teacher.get_full_name() or child.teacher.username,
			"total_quizzes_attempted": attempts.count(),
			"completed_quizzes": completed_attempts.count(),
			"incomplete_quizzes": attempts.filter(is_completed=False).count(),
			"average_score_percentage": round(avg_percentage, 2),
			"highest_score_percentage": round(max(percentages) if percentages else 0, 2),
			"lowest_score_percentage": round(min(percentages) if percentages else 0, 2),
			"total_marks_earned": total_marks_earned,
			"total_possible_marks": total_possible_marks,
			"recent_performance_trend": trend,
			"last_quiz_date": attempts.first().attempted_at if attempts.exists() else None,
			"performance_level": self._get_performance_level(avg_percentage)
		}

	def _calculate_trend(self, attempts):
		"""Calculate performance trend based on recent attempts"""
		if len(attempts) < 3:
			return "insufficient_data"

		# Split into recent vs older attempts
		recent = attempts[:3]
		older = attempts[3:6] if len(attempts) >= 6 else attempts[3:]

		if not older:
			return "insufficient_data"

		recent_avg = sum(a.percentage for a in recent) / len(recent)
		older_avg = sum(a.percentage for a in older) / len(older)

		diff = recent_avg - older_avg

		if diff > 5:
			return "improving"
		elif diff < -5:
			return "declining"
		else:
			return "stable"

	def _get_performance_level(self, percentage):
		"""Get performance level based on percentage"""
		if percentage >= 90:
			return "Excellent"
		elif percentage >= 80:
			return "Very Good"
		elif percentage >= 70:
			return "Good"
		elif percentage >= 60:
			return "Fair"
		else:
			return "Needs Improvement"

	def _get_performance_trends(self, attempts):
		"""Get performance trends over time"""
		completed_attempts = attempts.filter(is_completed=True).order_by('attempted_at')

		if not completed_attempts.exists():
			return {"monthly": [], "weekly": []}

		# Monthly trends
		monthly_data = {}
		weekly_data = {}

		for attempt in completed_attempts:
			# Monthly grouping
			month_key = attempt.attempted_at.strftime('%Y-%m')
			if month_key not in monthly_data:
				monthly_data[month_key] = {'attempts': [], 'period': month_key}
			monthly_data[month_key]['attempts'].append(attempt)

			# Weekly grouping (ISO week)
			year, week, _ = attempt.attempted_at.isocalendar()
			week_key = f"{year}-W{week:02d}"
			if week_key not in weekly_data:
				weekly_data[week_key] = {'attempts': [], 'period': week_key}
			weekly_data[week_key]['attempts'].append(attempt)

		# Process monthly data
		monthly_trends = []
		for period, data in sorted(monthly_data.items()):
			attempts_list = data['attempts']
			percentages = [a.percentage for a in attempts_list]
			monthly_trends.append({
				"period": period,
				"average_percentage": round(sum(percentages) / len(percentages), 2),
				"quizzes_taken": len(attempts_list),
				"total_marks": sum(a.score for a in attempts_list),
				"possible_marks": sum(a.total_marks for a in attempts_list)
			})

		# Process weekly data (last 8 weeks only)
		weekly_trends = []
		for period, data in sorted(weekly_data.items())[-8:]:
			attempts_list = data['attempts']
			percentages = [a.percentage for a in attempts_list]
			weekly_trends.append({
				"period": period,
				"average_percentage": round(sum(percentages) / len(percentages), 2),
				"quizzes_taken": len(attempts_list),
				"total_marks": sum(a.score for a in attempts_list),
				"possible_marks": sum(a.total_marks for a in attempts_list)
			})

		return {
			"monthly": monthly_trends,
			"weekly": weekly_trends
		}


class ParentChildQuizAttemptDetailView(APIView):
	"""
	GET /api/parent/performance/child/{child_id}/quiz/{attempt_id}/ - Get detailed quiz attempt results
	"""
	permission_classes = [IsAuthenticated]

	def get(self, request, child_id, attempt_id):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)

		try:
			child = Student.objects.get(id=child_id, parent=request.user)
			attempt = QuizAttempt.objects.select_related('quiz').prefetch_related('answers__question').get(
				id=attempt_id,
				student=child
			)
		except (Student.DoesNotExist, QuizAttempt.DoesNotExist):
			return Response({"error": "Quiz attempt not found"}, status=404)

		# Get detailed quiz attempt data
		attempt_data = QuizAttemptPerformanceSerializer(attempt).data

		# Get question-by-question breakdown
		answers = attempt.answers.select_related('question').all()
		question_breakdown = []

		for answer in answers:
			question_breakdown.append({
				"question_id": answer.question.id,
				"question_text": answer.question.question_text,
				"option_a": answer.question.option_a,
				"option_b": answer.question.option_b,
				"option_c": answer.question.option_c,
				"option_d": answer.question.option_d,
				"correct_option": answer.question.correct_option,
				"selected_option": answer.selected_option,
				"is_correct": answer.is_correct,
				"marks": answer.question.marks,
				"marks_earned": answer.question.marks if answer.is_correct else 0
			})

		# Add unanswered questions
		answered_question_ids = [answer.question.id for answer in answers]
		unanswered_questions = attempt.quiz.questions.exclude(id__in=answered_question_ids)

		for question in unanswered_questions:
			question_breakdown.append({
				"question_id": question.id,
				"question_text": question.question_text,
				"option_a": question.option_a,
				"option_b": question.option_b,
				"option_c": question.option_c,
				"option_d": question.option_d,
				"correct_option": question.correct_option,
				"selected_option": None,
				"is_correct": False,
				"marks": question.marks,
				"marks_earned": 0
			})

		return Response({
			"attempt_details": attempt_data,
			"question_breakdown": question_breakdown,
			"summary": {
				"total_questions": len(question_breakdown),
				"answered_questions": len(answers),
				"correct_answers": len([a for a in answers if a.is_correct]),
				"incorrect_answers": len([a for a in answers if not a.is_correct]),
				"unanswered_questions": len(unanswered_questions),
				"total_marks_possible": attempt.total_marks,
				"marks_earned": attempt.score,
				"percentage": attempt.percentage
			}
		})
