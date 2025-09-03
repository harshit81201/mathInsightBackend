
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Student
from .serializers import StudentSerializer, StudentCreateSerializer
from users.models import User

class StudentListCreateView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		students = Student.objects.filter(teacher=request.user)
		return Response(StudentSerializer(students, many=True).data)
	def post(self, request):
		serializer = StudentCreateSerializer(data=request.data, context={"request": request})
		serializer.is_valid(raise_exception=True)
		student = serializer.save()
		return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)

class StudentRetrieveUpdateDeleteView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, pk):
		try:
			student = Student.objects.get(pk=pk, teacher=request.user)
		except Student.DoesNotExist:
			return Response({"error": "Not found"}, status=404)
		return Response(StudentSerializer(student).data)
	def patch(self, request, pk):
		try:
			student = Student.objects.get(pk=pk, teacher=request.user)
		except Student.DoesNotExist:
			return Response({"error": "Not found"}, status=404)
		from .serializers import StudentUpdateSerializer
		serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		# Return clean response with StudentSerializer
		return Response(StudentSerializer(student).data)
	def delete(self, request, pk):
		try:
			student = Student.objects.get(pk=pk, teacher=request.user)
		except Student.DoesNotExist:
			return Response({"error": "Not found"}, status=404)
		parent = student.parent
		student.delete()
		# If parent has no more children, delete parent
		if not parent.children.exists():
			parent.delete()
		return Response(status=204)
