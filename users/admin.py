from django.contrib import admin
from .models import User

admin.site.register(User)





from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # Обновляет refresh_token при каждом обновлении access_token
    "BLACKLIST_AFTER_ROTATION": True,  # Блокирует старый refresh_token
    "AUTH_HEADER_TYPES": ("Bearer",),
}
