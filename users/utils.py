import os

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


def send_message_email(user_first_name, user_email, message, subject="EduTube mail", url_link=None):
    """
    Функция для отправки письма.

    :param user_email:
    :param user_first_name: Имя пользователя
    :param url_link:
    :param subject:
    :param message:
    """
    # Send activation email
    message_html = render_to_string("users/message_email.html", {
        "user_first_name": user_first_name,
        "message": message,
        "url_link": url_link
    })

    email = EmailMultiAlternatives(
        subject,
        None,  # Message text fallback is auto-generated
        settings.DEFAULT_FROM_EMAIL,
        [user_email]
    )
    email.attach_alternative(message_html, "text/html")
    email.send()


def send_activation_email(user, subject="Activate Your Account"):
    """
    Функция для отправки письма активации пользователя.

    :param subject:
    :param user: Объект пользователя
    """
    # Дополнительно: отправка письма подтверждения Generate activation token and UID
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Prepare activation URL
    activation_url = f"{os.getenv('FRONTEND_URL')}/auth/activate/{uid}/{token}/"

    # Send activation email
    message_html = render_to_string("users/activation_email.html", {
        "user": user,
        "activation_url": activation_url
    })

    email = EmailMultiAlternatives(
        subject,
        None,   # Message text fallback is auto-generated
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(message_html, "text/html")
    email.send()
