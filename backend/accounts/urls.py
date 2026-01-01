from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('profile/', views.profile),
    path('update-profile/', views.update_profile),
    path('users/', views.list_users),
    path('change-role/', views.change_role),
    
    # Réinitialisation de mot de passe
    path('request-password-reset/', views.request_password_reset),
    path('verify-reset-code/', views.verify_reset_code),
    path('reset-password/', views.reset_password),

    # JWT
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
