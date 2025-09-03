"""
students/urls.py
Defines student CRUD endpoints as per API_SPEC.md.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', views.StudentRetrieveUpdateDeleteView.as_view(), name='student-detail'),
]
