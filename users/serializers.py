from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed

from django.utils.timezone import now
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

from .models import User
from .utils import send_activation_email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        # Базовая валидация
        data = super().validate(attrs)

        # Достаем текущего пользователя (после успешной аутентификации он доступен в self.user)
        user = self.user

        # Обновляем поле last_login для пользователя
        user.last_login = now()
        user.save(update_fields=["last_login"])  # Сохраняем только last_login для повышения производительности

        # Добавляем информацию об оставшемся времени токенов
        access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
        refresh_token_lifetime = api_settings.REFRESH_TOKEN_LIFETIME

        # Расчет оставшегося времени (timezone-aware)
        current_time = now()
        access_exp_time = (current_time + access_token_lifetime).isoformat()
        refresh_exp_time = (current_time + refresh_token_lifetime).isoformat()

        # Включаем оставшееся время в ответ
        data["access_token_expires_in"] = access_token_lifetime.total_seconds()
        data["refresh_token_expires_in"] = refresh_token_lifetime.total_seconds()
        data["access_token_expires_at"] = access_exp_time
        data["refresh_token_expires_at"] = refresh_exp_time

        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # Базовая валидация токена
        data = super().validate(attrs)

        # Проверяем, делает ли ротацию refresh-токен
        rotate_refresh = api_settings.ROTATE_REFRESH_TOKENS

        # Информация о времени токенов
        access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
        refresh_token_lifetime = api_settings.REFRESH_TOKEN_LIFETIME if rotate_refresh else None

        # Текущее время
        current_time = now()

        # Добавляем информацию об access токене
        access_info = self.add_token_lifetime_info(access_token_lifetime, "access_token", current_time)
        data.update(access_info)

        # Добавляем информацию о refresh токене (если используется ротация)
        if rotate_refresh:
            refresh_info = self.add_token_lifetime_info(refresh_token_lifetime, "refresh_token", current_time)
            data.update(refresh_info)

        return data

    @staticmethod
    def add_token_lifetime_info(lifetime, key_prefix, current_time):
        """
        Вспомогательный метод для расчета времени токена.
        """
        exp_time = (current_time + lifetime).isoformat()
        return {
            f"{key_prefix}_expires_in": lifetime.total_seconds(),
            f"{key_prefix}_expires_at": exp_time,
        }







class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о пользователе."""

    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'first_name', 'last_name', 'is_active')


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name')

    # def validate(self, data):
    #     # Проверка совпадения пароля
    #     if data['password'] != data['confirm_password']:
    #         raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
    #
    #     # Уникальность email
    #     if User.objects.filter(email=data['email']).exists():
    #         raise serializers.ValidationError({"email": "A user is already registered with this email address."})
    #
    #     return data


    def validate(self, data):
        # Check if passwords match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if User.objects.filter(email=data['email']).exists():
            if User.objects.filter(email=data['email'], is_active=False).exists():
                raise serializers.ValidationError({
                    "email": "An account with this email is awaiting activation. Please check your email."
                })
            else:
                raise serializers.ValidationError({"email": "A user is already registered with this email address."})

        return data


    def create(self, validated_data):
        # print(validated_data)
        # Удалите поле confirm_password перед созданием пользователя
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        # Создаем нового пользователя
        user = User.objects.create_user(password=password, **validated_data)

        send_activation_email(user)

        return user


class RoleChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        extra_kwargs = {
            'role': {'required': True}
        }

    def validate_role(self, value):
        if value not in ['teacher', 'student']:
            raise serializers.ValidationError("You can only switch to 'teacher' or 'student'.")
        return value

