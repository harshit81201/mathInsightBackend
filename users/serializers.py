
"""
users/serializers.py
Serializers for authentication and user endpoints.
"""
from rest_framework import serializers
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from .models import User
from students.models import Student
from quizzes.models import QuizAttempt, QuizAnswer

class TeacherRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    schoolName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phoneNumber = serializers.CharField(write_only=True, required=False, allow_blank=True)
    firstName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    lastName = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "firstName", "lastName", "schoolName", "phoneNumber"]

    def create(self, validated_data):
        school_name = validated_data.pop("schoolName", "")
        phone_number = validated_data.pop("phoneNumber", "")
        first_name = validated_data.pop("firstName", validated_data.get("first_name", ""))
        last_name = validated_data.pop("lastName", validated_data.get("last_name", ""))
        user = User(
            email=validated_data["email"],
            username=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
            role="teacher",
            school_name=school_name,
            phone_number=phone_number,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "first_name", "last_name", "school_name"]

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


# Parent Performance Serializers

class QuizAttemptPerformanceSerializer(serializers.ModelSerializer):
    """Detailed quiz attempt with performance metrics"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_description = serializers.CharField(source='quiz.description', read_only=True)
    quiz_total_marks = serializers.IntegerField(source='quiz.total_marks', read_only=True)
    quiz_total_questions = serializers.IntegerField(source='quiz.total_questions', read_only=True)
    teacher_name = serializers.CharField(source='quiz.teacher.get_full_name', read_only=True)
    percentage = serializers.ReadOnlyField()
    correct_answers = serializers.SerializerMethodField()
    incorrect_answers = serializers.SerializerMethodField()
    unanswered_questions = serializers.SerializerMethodField()
    time_taken_display = serializers.SerializerMethodField()
    performance_level = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz_title', 'quiz_description', 'quiz_total_marks',
            'quiz_total_questions', 'teacher_name', 'score', 'total_marks',
            'percentage', 'correct_answers', 'incorrect_answers',
            'unanswered_questions', 'attempted_at', 'completed_at',
            'is_completed', 'time_taken_display', 'performance_level'
        ]

    def get_correct_answers(self, obj):
        return obj.answers.filter(is_correct=True).count()

    def get_incorrect_answers(self, obj):
        return obj.answers.filter(is_correct=False).count()

    def get_unanswered_questions(self, obj):
        answered_count = obj.answers.count()
        total_questions = obj.quiz.total_questions
        return total_questions - answered_count

    def get_time_taken_display(self, obj):
        if obj.completed_at and obj.attempted_at:
            duration = obj.completed_at - obj.attempted_at
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        return "Incomplete"

    def get_performance_level(self, obj):
        percentage = obj.percentage
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


class ChildPerformanceSummarySerializer(serializers.Serializer):
    """Summary performance statistics for a child"""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    class_name = serializers.CharField()
    teacher_name = serializers.CharField()
    total_quizzes_attempted = serializers.IntegerField()
    completed_quizzes = serializers.IntegerField()
    incomplete_quizzes = serializers.IntegerField()
    average_score_percentage = serializers.FloatField()
    highest_score_percentage = serializers.FloatField()
    lowest_score_percentage = serializers.FloatField()
    total_marks_earned = serializers.IntegerField()
    total_possible_marks = serializers.IntegerField()
    recent_performance_trend = serializers.CharField()  # "improving", "declining", "stable"
    last_quiz_date = serializers.DateTimeField(allow_null=True)
    performance_level = serializers.CharField()


class ChildDetailedPerformanceSerializer(serializers.Serializer):
    """Detailed performance data for a specific child"""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    class_name = serializers.CharField()
    teacher_name = serializers.CharField()
    performance_summary = ChildPerformanceSummarySerializer()
    quiz_attempts = QuizAttemptPerformanceSerializer(many=True)
    performance_trends = serializers.DictField()  # Monthly/weekly trends


class PerformanceTrendDataSerializer(serializers.Serializer):
    """Performance trend data over time"""
    period = serializers.CharField()  # "2024-01", "Week 1", etc.
    average_percentage = serializers.FloatField()
    quizzes_taken = serializers.IntegerField()
    total_marks = serializers.IntegerField()
    possible_marks = serializers.IntegerField()


class AllChildrenPerformanceSerializer(serializers.Serializer):
    """Performance overview for all parent's children"""
    children_count = serializers.IntegerField()
    overall_statistics = serializers.DictField()
    children_performance = ChildPerformanceSummarySerializer(many=True)
