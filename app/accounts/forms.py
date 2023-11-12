from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms.fields import EmailField
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form created to change the label of the email field to "Email Address".
    """
    email = forms.EmailField(
        label=_("Email Address"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form made to allow users to register using an email and password.
    """
    email = forms.EmailField(label='Email Address')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        """Determines which fields are displayed. Username field does not need to be in the form therefore it's
        excluded."""
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        """Checks to see if the email already exists in the database"""
        email = self.cleaned_data['email'].lower()
        new = User.objects.filter(email=email)
        if new.count():
            raise ValidationError(" Email Already Exists")
        return email

    def clean_password2(self):
        """Checks if the passwords match."""
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """Saves the registered user using username/email/password. The username is the same as email at the moment
        but that may be changed at a later date."""
        user = User.objects.create_user(
            self.cleaned_data['email'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        user.is_active = False
        user.save()
        return user


class CustomAuthenticationForm(forms.Form):
    """
    Custom authentication form to accept email/password login credentials.
    """

    email = EmailField(label=_("Email Address"), widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(email)s and password. If this is a new account make sure that you have verified your email."
        ),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "email" field.
        self.email_field = User._meta.get_field(User.EMAIL_FIELD)
        email_max_length = self.email_field.max_length or 254
        self.fields["email"].max_length = email_max_length
        self.fields["email"].widget.attrs["maxlength"] = email_max_length
        if self.fields["email"].label is None:
            self.fields["email"].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        """Attempts to authenticate the user using the provided credentials. Also checks if the user's email is
        verified."""
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"email": self.email_field.verbose_name},
        )
