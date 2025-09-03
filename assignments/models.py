from django.db import models
from students.models import Student

class Assignment(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignments')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.title} for {self.student.name}"
