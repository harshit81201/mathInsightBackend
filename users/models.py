from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	ROLE_CHOICES = [
		("teacher", "Teacher"),
		("parent", "Parent"),
	]
	role = models.CharField(max_length=16, choices=ROLE_CHOICES)
	school_name = models.CharField(max_length=255, blank=True, null=True)
	phone_number = models.CharField(max_length=32, blank=True, null=True)

	def __str__(self) -> str:
		return f"{self.username} ({self.role})"
