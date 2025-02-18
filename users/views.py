from rest_framework import generics, status
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .serializers import RegistrationSerializer
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class RegisterUserView(generics.CreateAPIView):
    """
    Представление для регистрации пользователя.
    """
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Проверяем данные, если невалидно — возвращает 400 ошибку

        email = serializer.validated_data['email']

        # Проверяем, существует ли пользователь с данным email
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Сохраняем пользователя с `is_active=False`
        user = serializer.save(is_active=False)

        # Генерация токена для подтверждения email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # id пользователя в base64

        # Генерация URL для активации
        activation_url = request.build_absolute_uri(reverse('users:activate', args=[uid, token]))

        # Отправка письма
        subject = "Activate Your Account"
        message = render_to_string(
            'users/activation_email.html',
            {'user': user, 'activation_url': activation_url}
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "User registered successfully. Check your email for the activation link."},
            status=status.HTTP_201_CREATED,
        )


class ActivateUserView(APIView):
    """
    Представление для активации пользователя.
    """

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, что токен валиден
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        # Активируем пользователя
        user.is_active = True
        user.save()

        return Response({"message": "Account successfully activated!"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    Вход пользователя с проверкой email и пароля и выдачей JWT-токенов.
    """

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Проверяем email и пароль через стандартный метод Django
        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "This account is not active. Please activate your account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Генерация JWT-токенов
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class CheckUserView(APIView):
    """
    Представление для проверки, существует ли пользователь с указанным email.
    """

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)

        # Проверяем, передан ли email
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, существует ли пользователь
        user_exists = User.objects.filter(email=email).exists()

        return Response({"exists": user_exists}, status=status.HTTP_200_OK)


class SetRoleView(APIView):
    """
    Представление для установки роли пользователя при первом входе.
    """
    permission_classes = [IsAuthenticated]  # Требуется аутентификация

    def post(self, request, *args, **kwargs):
        user = request.user  # Получаем текущего аутентифицированного пользователя
        role = request.data.get('role', None)

        # Проверяем, была ли уже установлена роль
        if user.role:
            return Response(
                {"error": "Role has already been set."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, передана ли роль
        if not role:
            return Response(
                {"error": "Role is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, что роль корректна (student или teacher)
        if role not in ['student', 'teacher']:
            return Response(
                {"error": "Invalid role. Role must be either 'student' or 'teacher'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Устанавливаем роль
        user.role = role
        user.save()  # Сохраняем изменения

        return Response(
            {"message": "Role has been successfully set.", "role": role},
            status=status.HTTP_200_OK
        )


class GetCurrentRoleView(APIView):
    """
    Представление для получения текущей роли пользователя.
    """
    permission_classes = [IsAuthenticated]  # Доступ только для авторизованных пользователей

    def get(self, request, *args, **kwargs):
        user = request.user  # Получаем текущего аутентифицированного пользователя

        # Проверяем, установлена ли роль у пользователя
        if not user.role:
            return Response(
                {"message": "Role is not set yet."},
                status=status.HTTP_200_OK
            )

        # Возвращаем текущую роль
        return Response(
            {"role": user.role},
            status=status.HTTP_200_OK
        )


class SwitchRoleView(APIView):
    """
    Представление для переключения роли между student и teacher.
    """
    permission_classes = [IsAuthenticated]  # Доступ только для авторизованных пользователей

    def post(self, request, *args, **kwargs):
        user = request.user  # Получаем текущего аутентифицированного пользователя

        if not user.role:
            return Response(
                {"error": "Role is not set. Please set a role first using `set-role/`."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role not in ['student', 'teacher']:
            return Response(
                {"error": "Invalid role in database."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Переключаем роль
        new_role = 'teacher' if user.role == 'student' else 'student'
        user.role = new_role
        user.save()  # Сохраняем изменения

        return Response(
            {"message": "Role switched successfully.", "new_role": new_role},
            status=status.HTTP_200_OK
        )