"""
assignments/urls.py
Defines assignment endpoints as per API_SPEC.md.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('assignments/', views.AssignmentListView.as_view(), name='assignment-list'),
]
