"""
URL configuration for simulation_mods project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
urlpatterns = [
    path('signup/',views.user_signup,name="user_signup"),
    path('email-verification/',views.email_verification,name="email_verification"),
    path('verify-email/<uidb64>/<token>/',views.email_verification,name="verify_email"),
    path('login/',views.user_login,name="user_login"),
    path('logout/',views.user_logout,name="user_logout"),
    path('forgot-password/',views.forgot_password,name="forgot_password"),
    path('otp-verify/',views.otp_verify,name="otp_verify"),
    path('resend-otp/',views.resend_otp,name="resend_otp"),
    path('reset-password/',views.reset_password,name="reset_password")
]
