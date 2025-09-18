from rest_framework import serializers
from django.utils import timezone
from .models import Quiz, Question, QuizAttempt, QuizAnswer
from students.models import Student


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions - excludes correct_option for students"""

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'marks']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Include correct_option only for teachers
        if request and hasattr(request, 'user') and request.user.role == 'teacher':
            data['correct_option'] = instance.correct_option

        return data


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating questions - includes correct_option"""

    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for quiz list view"""
    total_questions = serializers.ReadOnlyField()
    total_marks = serializers.ReadOnlyField()
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    time_limit = serializers.IntegerField(source='time_limit_minutes', read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'time_limit', 'deadline',
            'is_active', 'total_questions', 'total_marks', 'teacher_name', 'created_at'
        ]


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz detail view"""
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.ReadOnlyField()
    total_marks = serializers.ReadOnlyField()
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    time_limit = serializers.IntegerField(source='time_limit_minutes', read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'time_limit', 'deadline',
            'is_active', 'questions', 'total_questions', 'total_marks',
            'teacher_name', 'created_at'
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating quizzes"""
    time_limit = serializers.IntegerField(write_only=True, source='time_limit_minutes')
    deadline = serializers.DateTimeField()

    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'deadline', 'is_active']

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value

    def create(self, validated_data):
        # Set the teacher to the current user
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class QuizUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating quizzes"""
    time_limit = serializers.IntegerField(write_only=True, source='time_limit_minutes', required=False)

    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'deadline', 'is_active']

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage = serializers.ReadOnlyField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'student', 'student_name', 'quiz_title',
            'score', 'total_marks', 'percentage', 'attempted_at',
            'completed_at', 'is_completed'
        ]
        read_only_fields = ['score', 'total_marks', 'attempted_at', 'completed_at', 'is_completed']


class QuizAnswerSerializer(serializers.ModelSerializer):
    """Serializer for individual quiz answers"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    correct_option = serializers.CharField(source='question.correct_option', read_only=True)
    marks = serializers.IntegerField(source='question.marks', read_only=True)

    class Meta:
        model = QuizAnswer
        fields = [
            'question', 'question_text', 'selected_option',
            'correct_option', 'is_correct', 'marks'
        ]


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submission"""
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        help_text="List of answers in format [{'question_id': '1', 'selected_option': 'A'}, ...]"
    )

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer is required.")

        for answer in value:
            if 'question_id' not in answer or 'selected_option' not in answer:
                raise serializers.ValidationError("Each answer must have 'question_id' and 'selected_option'.")

            if answer['selected_option'] not in ['A', 'B', 'C', 'D']:
                raise serializers.ValidationError("Selected option must be A, B, C, or D.")

        return value


class QuizResultSerializer(serializers.Serializer):
    """Serializer for quiz results"""
    attempt_id = serializers.IntegerField()
    quiz_title = serializers.CharField()
    student_name = serializers.CharField()
    score = serializers.IntegerField()
    total_marks = serializers.IntegerField()
    percentage = serializers.FloatField()
    attempted_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField()
    answers = QuizAnswerSerializer(many=True)


class ParentQuizListSerializer(serializers.ModelSerializer):
    """Serializer for parent quiz list - only active quizzes"""
    total_questions = serializers.ReadOnlyField()
    total_marks = serializers.ReadOnlyField()
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    time_limit = serializers.IntegerField(source='time_limit_minutes', read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'time_limit', 'deadline',
            'is_active', 'total_questions', 'total_marks', 'teacher_name'
        ]


class StudentScoreSummarySerializer(serializers.Serializer):
    """Serializer for student score summary"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    parent_email = serializers.EmailField()
    class_name = serializers.CharField()
    total_quizzes_attempted = serializers.IntegerField()
    average_score_percentage = serializers.FloatField()
    latest_quiz_date = serializers.DateTimeField(allow_null=True)
    completed_attempts = serializers.IntegerField()
    incomplete_attempts = serializers.IntegerField()


class QuizAttemptDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed quiz attempt with question statistics"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_total_marks = serializers.IntegerField(source='quiz.total_marks', read_only=True)
    quiz_total_questions = serializers.IntegerField(source='quiz.total_questions', read_only=True)
    correct_answers = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    quiz_marks = serializers.IntegerField(source='score', read_only=True)
    percentage = serializers.ReadOnlyField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz_title', 'quiz_total_marks', 'quiz_total_questions',
            'correct_answers', 'total_questions', 'quiz_marks', 'total_marks',
            'percentage', 'attempted_at', 'completed_at', 'is_completed'
        ]

    def get_correct_answers(self, obj):
        """Get number of correct answers for this attempt"""
        return obj.answers.filter(is_correct=True).count()

    def get_total_questions(self, obj):
        """Get total number of questions answered"""
        return obj.answers.count()


class StudentDetailedScoresSerializer(serializers.Serializer):
    """Serializer for detailed student scores"""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_email = serializers.EmailField()
    class_name = serializers.CharField()
    quiz_attempts = QuizAttemptDetailSerializer(many=True)


class AllQuizzesAttemptedSerializer(serializers.ModelSerializer):
    """Serializer for showing all quiz attempts by all students"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_class = serializers.CharField(source='student.class_name', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage = serializers.ReadOnlyField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student_name', 'student_class', 'quiz_title',
            'score', 'total_marks', 'percentage', 'attempted_at',
            'completed_at', 'is_completed'
        ]
