import os

from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, \
    CustomTokenRefreshSerializer, RoleChangeSerializer
from .models import User
from .permissions import IsNotAdmin
from .utils import send_activation_email, send_message_email


class DeleteUserView(APIView):
    # permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Получаем текущего пользователя
        user = request.user

        # Получаем пароль из тела запроса
        password = request.data.get("password")

        # Проверяем, указан ли пароль
        if not password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем совпадение пароля
        if not check_password(password, user.password):
            return Response({"error": "Password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Удаляем аккаунт пользователя
        user.delete()
        return Response({"success": "Account deleted successfully."}, status=status.HTTP_200_OK)


# 🔹 Выход (удаление refresh_token)
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginThrottle(UserRateThrottle):
    scope = 'login'


# 🔹 Кастомный логин (возвращает access и refresh)
class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


# 🔹 Обновление токена (используется Next.js)
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class EmailCheckThrottle(UserRateThrottle):
    scope = 'email_check'


class CheckUserView(APIView):
    """
    A view to check if a user with a specific email exists
    and provide additional information if necessary.
    """
    throttle_classes = [EmailCheckThrottle]
    permission_classes = [AllowAny]

    def get(self, request, email='', *args, **kwargs):
        # Validate that email is provided and valid
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a user with the given email exists
        try:
            user = User.objects.get(email=email)

            if not user.is_active:
                return Response({"error": "Read your mails, you need to activate account."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "User with this email exists."
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "No user found with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CancelActivateDeleteUserView(APIView):
    """
    View to cancel activate a user account when they click the link from the activation email.
    """
    permission_classes = [AllowAny]

    def delete(self, request, uidb64, email='', *args, **kwargs):
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the uidb64 to get the user ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check if user exists
        if user is not None:
            if user.email != email:
                return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
            if user.is_active:
                return Response({"error": "User is already active"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                first_name = user.first_name
                user.delete()  # Удаляет пользователя из базы
                send_message_email(user_first_name=first_name, user_email=email, subject="Account deleted", message="Your account has been deleted successfully. If you want to register go by link below. We hope to see you again soon.", url_link=f"{os.getenv('FRONTEND_URL')}/auth/register" )

                return Response({"success": "Account successfully deleted."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "Invalid cancel activation link."}, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    """
    View to activate a user account when they click the link from the activation email.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        # Get password from request data
        password = request.data.get("password", '')

        if not password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the uidb64 to get the user ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check if user exists
        if user is not None:
            if user.is_active:
                return Response({"error": "User is already active"}, status=status.HTTP_400_BAD_REQUEST)
            # Check token is valid
            elif not default_token_generator.check_token(user, token):
                send_activation_email(user, "Try activate your account again")
                return Response({"message": "Your link is expired, we have sent a new activation link to your email."}, status=status.HTTP_400_BAD_REQUEST)
            # Проверить, совпадает ли введённый пароль с существующим паролем в базе
            elif check_password(password, user.password):
                # Активировать пользователя
                user.is_active = True
                user.save()
                send_message_email(user_first_name=user.first_name, user_email=user.email, subject="Account activated", message="Your account has been activated successfully. Thank you for your patience. You can go to login by this link.", url_link=f"{os.getenv('FRONTEND_URL')}/auth/login")

                return Response({"success": "Account activated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)







# 🔹 Получение данных пользователя
class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"id": request.user.id, "email": request.user.email, "first_name": request.user.first_name, "last_name": request.user.last_name, "role": request.user.role, "isActivated": request.user.is_active})

        # user = request.user  # Получаем текущего пользователя
        # serializer = UserSerializer(user)  # Сериализуем данные пользователя
        # return Response(serializer.data)

class RegisterThrottle(UserRateThrottle):
    scope = 'registration'

class RegisterUserView(generics.CreateAPIView):
    """
    View to handle user registration. Saves the user with `is_active=False`
    and sends an activation email.
    """
    throttle_classes = [RegisterThrottle]
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({"success": "User registered successfully. Please verify your email."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = RoleChangeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Role updated successfully", "role": serializer.data['role']})
        return Response(serializer.errors, status=400)








# class LoginView(APIView):
#     """
#     User login with JWT tokens stored in HttpOnly cookies.
#     """
#     throttle_classes = [LoginThrottle]
#
#     def post(self, request, *args, **kwargs):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # user = serializer.validated_data["user"]  # Используем уже аутентифицированного пользователя
#         access_token = serializer.validated_data["access_token"]
#         refresh_token = serializer.validated_data["refresh_token"]
#
#         # Настройки куки
#         secure_cookie = settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"] if not settings.DEBUG else False
#
#         response = Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
#
#         response.set_cookie(
#             key=settings.SIMPLE_JWT["AUTH_COOKIE"],
#             value=access_token,
#             httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
#             secure=secure_cookie,  # Теперь учитывается режим разработки
#             samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
#             max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
#             path="/"
#         )
#
#         response.set_cookie(
#             key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
#             value=refresh_token,
#             httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
#             secure=secure_cookie,
#             samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
#             max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
#             path="/users/token/refresh/"
#         )
#
#         return response


