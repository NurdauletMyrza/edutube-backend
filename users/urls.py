from django.urls import path
from .views import (
    RegisterUserView, ActivateUserView, LoginView, CheckUserView, SetRoleView, GetCurrentRoleView, SwitchRoleView
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('check-user/', CheckUserView.as_view(), name='check_user'),
    path('set-role/', SetRoleView.as_view(), name='set_role'),
    path('get-current-role/', GetCurrentRoleView.as_view(), name='get_current_role'),
    path('switch-role/', SwitchRoleView.as_view(), name='switch_role'),
]
