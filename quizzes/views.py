from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from .models import Quiz, Question, QuizAttempt, QuizAnswer
from .serializers import (
    QuizListSerializer, QuizDetailSerializer, QuizCreateSerializer, QuizUpdateSerializer,
    QuestionSerializer, QuestionCreateSerializer, QuizAttemptSerializer,
    QuizSubmissionSerializer, QuizResultSerializer, ParentQuizListSerializer,
    QuizAnswerSerializer
)
from students.models import Student


class IsTeacher(permissions.BasePermission):
    """Permission class to check if user is a teacher"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsParent(permissions.BasePermission):
    """Permission class to check if user is a parent"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'parent'


class QuizListCreateView(generics.ListCreateAPIView):
    """
    GET /api/quizzes/ - Teacher gets all their quizzes
    POST /api/quizzes/ - Teacher creates a quiz
    """
    permission_classes = [IsTeacher]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizCreateSerializer
        return QuizListSerializer

    def get_queryset(self):
        # Return only quizzes created by the current teacher
        return Quiz.objects.filter(teacher=self.request.user)


class QuizDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET /api/quizzes/{id}/ - Get quiz details
    PATCH /api/quizzes/{id}/ - Teacher updates quiz
    """
    permission_classes = [IsTeacher]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuizUpdateSerializer
        return QuizDetailSerializer

    def get_queryset(self):
        # Return only quizzes created by the current teacher
        return Quiz.objects.filter(teacher=self.request.user)


class QuestionListCreateView(generics.ListCreateAPIView):
    """
    GET /api/quizzes/{quiz_id}/questions/ - Get all questions for a quiz
    POST /api/quizzes/{quiz_id}/questions/ - Teacher adds questions to a quiz
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateSerializer
        return QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Teachers can see all questions, others can only see questions for active quizzes
        if self.request.user.role == 'teacher':
            # Teachers can only see questions for their own quizzes
            if quiz.teacher != self.request.user:
                return Question.objects.none()
        else:
            # Parents can only see questions for active quizzes
            if not quiz.is_active:
                return Question.objects.none()

        return Question.objects.filter(quiz=quiz)

    def perform_create(self, serializer):
        quiz_id = self.kwargs['quiz_id']
        quiz = get_object_or_404(Quiz, id=quiz_id, teacher=self.request.user)
        serializer.save(quiz=quiz)


class ParentQuizListView(generics.ListAPIView):
    """
    GET /api/parent/quizzes/ - Parent gets only active quizzes for their children
    """
    permission_classes = [IsParent]
    serializer_class = ParentQuizListSerializer

    def get_queryset(self):
        # Get active quizzes for children of the current parent
        parent = self.request.user
        children = Student.objects.filter(parent=parent)

        if not children.exists():
            return Quiz.objects.none()

        # Get quizzes taught by teachers of the parent's children that are active and not past deadline
        teacher_ids = children.values_list('teacher_id', flat=True).distinct()

        return Quiz.objects.filter(
            teacher_id__in=teacher_ids,
            is_active=True,
            deadline__gt=timezone.now()
        ).distinct()


@api_view(['POST'])
@permission_classes([IsParent])
def start_quiz_attempt(request, quiz_id):
    """
    POST /api/quizzes/{id}/attempt/ - Parent starts a quiz attempt for a child
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    parent = request.user

    # Check if quiz is active and not past deadline
    if not quiz.is_active:
        return Response(
            {'error': 'This quiz is not currently active.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if quiz.deadline <= timezone.now():
        return Response(
            {'error': 'This quiz has passed its deadline.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get student_id from request data
    student_id = request.data.get('student_id')
    if not student_id:
        return Response(
            {'error': 'student_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify the student belongs to this parent
    try:
        student = Student.objects.get(id=student_id, parent=parent)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found or not your child.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if student is taught by the quiz teacher
    if student.teacher != quiz.teacher:
        return Response(
            {'error': 'This quiz is not available for this student.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if student has already attempted this quiz
    if QuizAttempt.objects.filter(quiz=quiz, student=student).exists():
        return Response(
            {'error': 'This student has already attempted this quiz.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create quiz attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        student=student,
        parent=parent,
        total_marks=quiz.total_marks
    )

    serializer = QuizAttemptSerializer(attempt)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsParent])
def submit_quiz(request, quiz_id):
    """
    POST /api/quizzes/{id}/submit/ - Submit quiz answers and get immediate results
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    parent = request.user

    # Get student_id from request data
    student_id = request.data.get('student_id')
    if not student_id:
        return Response(
            {'error': 'student_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify the student belongs to this parent
    try:
        student = Student.objects.get(id=student_id, parent=parent)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found or not your child.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get the quiz attempt
    try:
        attempt = QuizAttempt.objects.get(quiz=quiz, student=student, parent=parent)
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Quiz attempt not found. Please start the quiz first.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if attempt.is_completed:
        return Response(
            {'error': 'This quiz has already been submitted.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate submission data
    submission_serializer = QuizSubmissionSerializer(data=request.data)
    if not submission_serializer.is_valid():
        return Response(
            submission_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    answers_data = submission_serializer.validated_data['answers']

    with transaction.atomic():
        total_score = 0
        quiz_answers = []

        # Process each answer
        for answer_data in answers_data:
            question_id = int(answer_data['question_id'])
            selected_option = answer_data['selected_option']

            try:
                question = Question.objects.get(id=question_id, quiz=quiz)
            except Question.DoesNotExist:
                return Response(
                    {'error': f'Question {question_id} not found in this quiz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create or update quiz answer
            quiz_answer, created = QuizAnswer.objects.get_or_create(
                attempt=attempt,
                question=question,
                defaults={'selected_option': selected_option}
            )

            if not created:
                quiz_answer.selected_option = selected_option
                quiz_answer.save()

            # Add to score if correct
            if quiz_answer.is_correct:
                total_score += question.marks

            quiz_answers.append(quiz_answer)

        # Update attempt with score and mark as completed
        attempt.score = total_score
        attempt.complete_attempt()

    # Return results
    result_data = {
        'attempt_id': attempt.id,
        'quiz_title': quiz.title,
        'student_name': student.name,
        'score': attempt.score,
        'total_marks': attempt.total_marks,
        'percentage': attempt.percentage,
        'attempted_at': attempt.attempted_at,
        'completed_at': attempt.completed_at,
        'answers': QuizAnswerSerializer(quiz_answers, many=True).data
    }

    serializer = QuizResultSerializer(data=result_data)
    serializer.is_valid()

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_quiz_results(request, quiz_id):
    """
    GET /api/quizzes/{id}/results/ - Get quiz results for a specific attempt
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user

    if user.role == 'teacher':
        # Teachers can see results for their quizzes
        if quiz.teacher != user:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all attempts for this quiz
        attempts = QuizAttempt.objects.filter(quiz=quiz, is_completed=True)
        results = []

        for attempt in attempts:
            answers = QuizAnswer.objects.filter(attempt=attempt)
            result_data = {
                'attempt_id': attempt.id,
                'quiz_title': quiz.title,
                'student_name': attempt.student.name,
                'score': attempt.score,
                'total_marks': attempt.total_marks,
                'percentage': attempt.percentage,
                'attempted_at': attempt.attempted_at,
                'completed_at': attempt.completed_at,
                'answers': QuizAnswerSerializer(answers, many=True).data
            }
            results.append(result_data)

        return Response(results, status=status.HTTP_200_OK)

    elif user.role == 'parent':
        # Parents can see results for their children
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id parameter is required for parents.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            student = Student.objects.get(id=student_id, parent=user)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found or not your child.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            attempt = QuizAttempt.objects.get(quiz=quiz, student=student, parent=user, is_completed=True)
        except QuizAttempt.DoesNotExist:
            return Response(
                {'error': 'Quiz results not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        answers = QuizAnswer.objects.filter(attempt=attempt)
        result_data = {
            'attempt_id': attempt.id,
            'quiz_title': quiz.title,
            'student_name': student.name,
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'percentage': attempt.percentage,
            'attempted_at': attempt.attempted_at,
            'completed_at': attempt.completed_at,
            'answers': QuizAnswerSerializer(answers, many=True).data
        }

        serializer = QuizResultSerializer(data=result_data)
        serializer.is_valid()

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        return Response(
            {'error': 'Permission denied.'},
            status=status.HTTP_403_FORBIDDEN
        )
