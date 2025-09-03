"""
students/serializers.py
Serializers for Student creation and update, including parent creation logic.
"""
from rest_framework import serializers
from .models import Student
from users.models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

class StudentSerializer(serializers.ModelSerializer):
    parent_details = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ["id", "name", "class_name", "parent_details"]
        read_only_fields = ["id", "parent_details"]

    def get_parent_details(self, obj):
        if obj.parent:
            return {
                "id": obj.parent.id,
                "email": obj.parent.email,
                "first_name": obj.parent.first_name,
                "last_name": obj.parent.last_name,
                "role": obj.parent.role
            }
        return None


class ParentChildrenSerializer(serializers.ModelSerializer):
    """Serializer for parent to view their children with teacher details"""
    teacher_details = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ["id", "name", "class_name", "teacher_details"]
        read_only_fields = ["id", "name", "class_name", "teacher_details"]

    def get_teacher_details(self, obj):
        if obj.teacher:
            return {
                "id": obj.teacher.id,
                "email": obj.teacher.email,
                "first_name": obj.teacher.first_name,
                "last_name": obj.teacher.last_name,
                "full_name": obj.teacher.get_full_name(),
                "school_name": obj.teacher.school_name
            }
        return None


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "name", "parent_name", "parent_email", "class_name"]
        read_only_fields = ["id"]

class StudentCreateSerializer(serializers.ModelSerializer):
    # Accept camelCase from frontend
    class_name = serializers.CharField(write_only=True, required=False)

    parent_name = serializers.CharField(write_only=True, required=False)

    parent_email = serializers.EmailField(write_only=True, required=False)


    class Meta:
        model = Student
        fields = ["id", "name", "parent_name", "parent_email", "class_name", "teacher", "temp_password"]
        read_only_fields = ["id", "temp_password", "teacher"]

    def create(self, validated_data):
        # Map camelCase to snake_case
        parent_email = validated_data["parent_email"]
        parent_name = validated_data["parent_name"]
        class_name = validated_data["class_name"]
        name = validated_data["name"]

        # Check if parent exists
        parent, created = User.objects.get_or_create(
            email=parent_email,
            defaults={
                "username": parent_email,
                "role": "parent",
                "first_name": parent_name,
            },
        )
        if created:
            temp_password = get_random_string(8)
            parent.set_password(temp_password)
            parent.save()
            # Send email to parent
            send_mail(
                subject="Your MathInsight Parent Account",
                message=f"Hello {parent_name},\n\nYour account has been created.\nEmail: {parent_email}\nTemporary password: {temp_password}",
                from_email=None,
                recipient_list=[parent_email],
                fail_silently=True,
            )
        else:
            temp_password = None
        student = Student.objects.create(
            name=name,
            parent_name=parent_name,
            parent_email=parent_email,
            class_name=class_name,
            parent=parent,
            teacher=self.context["request"].user,
            temp_password=temp_password,
        )
        return student
