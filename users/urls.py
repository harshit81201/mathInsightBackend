"""
users/urls.py
Defines authentication, teacher, and parent endpoints as per API_SPEC.md.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.TeacherRegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('teachers/<int:pk>/', views.TeacherProfileView.as_view(), name='teacher-profile'),
    path('teachers/<int:pk>/students/', views.TeacherStudentsView.as_view(), name='teacher-students'),
    path('parent/me/', views.ParentProfileView.as_view(), name='parent-me'),
    path('parent/children/', views.ParentChildrenView.as_view(), name='parent-children'),
]
