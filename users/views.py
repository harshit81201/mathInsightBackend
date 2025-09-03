from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, LoginSerializer, TeacherRegisterSerializer


class TeacherRegisterView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = TeacherRegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		from rest_framework_simplejwt.tokens import RefreshToken
		refresh = RefreshToken.for_user(user)
		return Response({
			"token": str(refresh.access_token),
			"user": UserSerializer(user).data
		}, status=201)


class LoginView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		email = serializer.validated_data["email"]
		password = serializer.validated_data["password"]
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
		user = authenticate(request, username=user.username, password=password)
		if not user:
			return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
		refresh = RefreshToken.for_user(user)
		token_str = str(refresh.access_token)
		print(f"LOGIN SUCCESS: {user.email}, Token: {token_str}")
		return Response({
			"token": token_str,
			"user": UserSerializer(user).data
		})

class MeView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		return Response(UserSerializer(request.user).data)

class TeacherProfileView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, pk):
		try:
			teacher = User.objects.get(pk=pk, role="teacher")
		except User.DoesNotExist:
			return Response({"error": "Teacher not found"}, status=404)
		return Response(UserSerializer(teacher).data)

class TeacherStudentsView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, pk):
		from students.models import Student
		from students.serializers import StudentSerializer
		students = Student.objects.filter(teacher_id=pk)
		return Response(StudentSerializer(students, many=True).data)

class ParentProfileView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)
		from students.models import Student
		children = Student.objects.filter(parent=request.user)
		data = UserSerializer(request.user).data
		data["children"] = [
			{"id": c.id, "name": c.name, "class_name": c.class_name} for c in children
		]
		return Response(data)

class ParentChildrenView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		if request.user.role != "parent":
			return Response({"error": "Not a parent"}, status=403)
		from students.models import Student
		children = Student.objects.filter(parent=request.user)
		return Response([{"id": c.id, "name": c.name, "class_name": c.class_name} for c in children])
