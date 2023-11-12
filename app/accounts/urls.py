from django.urls import path
from django.views.generic import TemplateView

from .views import SignUpView, CustomLoginView, activate, AccountView, CustomPasswordResetView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path('activate/<uidb64>/<token>', activate, name="activate"),
    path("info/", TemplateView.as_view(template_name="registration/account.html"), name="account")
]