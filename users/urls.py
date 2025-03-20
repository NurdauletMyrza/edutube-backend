from django.urls import path

from .views import (LogoutView, CustomTokenObtainPairView, CustomTokenRefreshView, UserDetailsView, CheckUserView,
                    RegisterUserView, ActivateUserView, RoleChangeView, DeleteUserView,
                    CancelActivateDeleteUserView)

app_name = 'users'

urlpatterns = [
    path("user/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("user/logout/", LogoutView.as_view(), name="user_logout"),
    path("user/details/", UserDetailsView.as_view(), name="user_details"),
    path('user/delete-user/', DeleteUserView.as_view(), name='delete_user'),

    path('check-user/<str:email>/', CheckUserView.as_view(), name='check_user'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate_user'),
    path('cancel-activation/<uidb64>/<str:email>/', CancelActivateDeleteUserView.as_view(), name='cancel_activate_user'),

    path('user/change-role/', RoleChangeView.as_view(), name='change-role'),
    path('register/', RegisterUserView.as_view(), name='register'),
    # path('me/', UserDetailsView.as_view(), name='user_details'),
    # path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
]
