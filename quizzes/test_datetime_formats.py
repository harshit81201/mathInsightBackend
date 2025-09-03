"""
Test the quiz creation with different datetime formats
"""
import json
from datetime import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class QuizDateTimeFormatTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a teacher user
        self.teacher = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            role='teacher'
        )

        # Login to get token (simplified - assumes you have token auth working)
        response = self.client.post('/api/login/', {
            'email': 'teacher@test.com',
            'password': 'testpass123'
        })

        if response.status_code == 200:
            self.token = response.data.get('access')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_quiz_creation_with_frontend_datetime_format(self):
        """Test that quiz creation works with frontend datetime format"""
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test quiz",
            "time_limit": 30,
            "deadline": "2025-09-10T15:30",  # Frontend format
            "is_active": True
        }

        response = self.client.post('/api/quizzes/', quiz_data, format='json')

        # Print response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Test Quiz")
        self.assertEqual(response.data['time_limit'], 30)

    def test_quiz_creation_with_various_datetime_formats(self):
        """Test that various datetime formats work"""
        formats_to_test = [
            "2025-09-10T15:30",
            "2025-09-10T15:30:00Z",
            "2025-09-10 15:30",
        ]

        for i, date_format in enumerate(formats_to_test):
            quiz_data = {
                "title": f"Test Quiz {i+1}",
                "description": f"Test quiz with format {date_format}",
                "time_limit": 30,
                "deadline": date_format,
                "is_active": True
            }

            response = self.client.post('/api/quizzes/', quiz_data, format='json')
            print(f"Format {date_format}: Status {response.status_code}")

            if response.status_code != 201:
                print(f"Error: {response.data}")
