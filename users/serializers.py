
"""
users/serializers.py
Serializers for authentication and user endpoints.
"""
from rest_framework import serializers
from .models import User

class TeacherRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    schoolName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phoneNumber = serializers.CharField(write_only=True, required=False, allow_blank=True)
    firstName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    lastName = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "firstName", "lastName", "schoolName", "phoneNumber"]

    def create(self, validated_data):
        school_name = validated_data.pop("schoolName", "")
        phone_number = validated_data.pop("phoneNumber", "")
        first_name = validated_data.pop("firstName", validated_data.get("first_name", ""))
        last_name = validated_data.pop("lastName", validated_data.get("last_name", ""))
        user = User(
            email=validated_data["email"],
            username=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
            role="teacher",
            school_name=school_name,
            phone_number=phone_number,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "first_name", "last_name", "school_name"]

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
