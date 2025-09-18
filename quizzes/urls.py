from django.urls import path
from . import views

urlpatterns = [
    # Teacher quiz management
    path('quizzes/', views.QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', views.QuizDetailUpdateView.as_view(), name='quiz-detail-update'),

    # Question management
    path('quizzes/<int:quiz_id>/questions/', views.QuestionListCreateView.as_view(), name='question-list-create'),

    # Parent quiz access
    path('parent/quizzes/', views.ParentQuizListView.as_view(), name='parent-quiz-list'),

    # Quiz attempts and submissions
    path('quizzes/<int:quiz_id>/attempt/', views.start_quiz_attempt, name='start-quiz-attempt'),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='submit-quiz'),
    path('quizzes/<int:quiz_id>/results/', views.get_quiz_results, name='quiz-results'),
    
    # Score endpoints for teachers
    path('scores/teacher/<int:teacher_id>/students/', views.teacher_students_scores, name='teacher-students-scores'),
    path('scores/teacher/<int:teacher_id>/student/<int:student_id>/', views.teacher_student_detailed_scores, name='teacher-student-detailed-scores'),
]
