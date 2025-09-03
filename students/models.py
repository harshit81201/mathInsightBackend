from django.db import models
from users.models import User

class Student(models.Model):
	name = models.CharField(max_length=100)
	parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children', limit_choices_to={'role': 'parent'})
	parent_name = models.CharField(max_length=100)
	parent_email = models.EmailField()
	class_name = models.CharField(max_length=50)
	teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students', limit_choices_to={'role': 'teacher'})
	temp_password = models.CharField(max_length=64, blank=True, null=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.class_name})"
