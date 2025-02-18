from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password', 'role']

    def validate(self, attrs):
        # Проверка подтверждения пароля
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Удаляем confirm_password из данных, так как оно не нужно для создания модели
        validated_data.pop('confirm_password')

        # Создаём пользователя, пароль будет автоматически хэширован
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Roles.NONE)  # Устанавливаем роль, если она передана
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Аутентификация пользователя
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({"error": "Invalid email or password."})

        # Проверка активности пользователя
        if not user.is_active:
            raise serializers.ValidationError({"error": "This account is inactive."})

        attrs['user'] = user
        return attrs
