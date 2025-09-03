from django.db import models
from django.utils import timezone
from users.models import User
from students.models import Student


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quizzes',
        limit_choices_to={'role': 'teacher'}
    )
    time_limit_minutes = models.PositiveIntegerField(help_text="Time limit in minutes")
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.teacher.get_full_name() or self.teacher.username}"

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_marks(self):
        return self.questions.aggregate(models.Sum('marks'))['marks__sum'] or 0


class Question(models.Model):
    OPTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Question for {self.quiz.title}: {self.question_text[:50]}..."


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='child_quiz_attempts',
        limit_choices_to={'role': 'parent'}
    )
    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['quiz', 'student']
        ordering = ['-attempted_at']

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title} ({self.score}/{self.total_marks})"

    @property
    def percentage(self):
        if self.total_marks == 0:
            return 0
        return round((self.score / self.total_marks) * 100, 2)

    def complete_attempt(self):
        """Mark the attempt as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


class QuizAnswer(models.Model):
    """Stores individual question answers for a quiz attempt"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=Question.OPTION_CHOICES)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt.student.name} - {self.question.question_text[:30]}... - {self.selected_option}"

    def save(self, *args, **kwargs):
        # Automatically determine if the answer is correct
        self.is_correct = self.selected_option == self.question.correct_option
        super().save(*args, **kwargs)
