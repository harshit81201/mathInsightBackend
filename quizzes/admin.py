from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, QuizAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    readonly_fields = ['question', 'selected_option', 'is_correct']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'is_active', 'deadline', 'total_questions', 'total_marks', 'created_at']
    list_filter = ['is_active', 'created_at', 'deadline', 'teacher']
    search_fields = ['title', 'description', 'teacher__username', 'teacher__email']
    readonly_fields = ['created_at', 'total_questions', 'total_marks']
    inlines = [QuestionInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'teacher')
        }),
        ('Quiz Settings', {
            'fields': ('time_limit_minutes', 'deadline', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_questions', 'total_marks', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teacher=request.user)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text_short', 'correct_option', 'marks']
    list_filter = ['quiz', 'correct_option', 'marks']
    search_fields = ['question_text', 'quiz__title']

    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(quiz__teacher=request.user)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'total_marks', 'percentage', 'is_completed', 'attempted_at']
    list_filter = ['is_completed', 'attempted_at', 'quiz']
    search_fields = ['student__name', 'quiz__title', 'parent__username']
    readonly_fields = ['percentage', 'attempted_at', 'completed_at']
    inlines = [QuizAnswerInline]

    fieldsets = (
        (None, {
            'fields': ('quiz', 'student', 'parent')
        }),
        ('Results', {
            'fields': ('score', 'total_marks', 'percentage', 'is_completed')
        }),
        ('Timestamps', {
            'fields': ('attempted_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(quiz__teacher=request.user)


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question_short', 'selected_option', 'correct_option', 'is_correct', 'marks']
    list_filter = ['is_correct', 'selected_option']
    search_fields = ['attempt__student__name', 'question__question_text']
    readonly_fields = ['is_correct']

    def question_short(self, obj):
        return obj.question.question_text[:30] + "..." if len(obj.question.question_text) > 30 else obj.question.question_text
    question_short.short_description = "Question"

    def correct_option(self, obj):
        return obj.question.correct_option
    correct_option.short_description = "Correct Option"

    def marks(self, obj):
        return obj.question.marks
    marks.short_description = "Marks"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(attempt__quiz__teacher=request.user)
