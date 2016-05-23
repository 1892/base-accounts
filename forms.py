from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    SetPasswordForm  # fill in custom user info then save it
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, ReadOnlyPasswordHashField, PasswordChangeForm
from .models import *
from django.contrib.auth import (
    get_user_model, password_validation,
)
from authtools import forms as authtoolsforms

User = get_user_model()


class BaseUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter Password'}),
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super(BaseUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': 'Username *'})
        self.fields['email'].widget = forms.TextInput(attrs={
            'placeholder': 'Email *'})
        self.fields['first_name'].widget = forms.TextInput(attrs={
            'placeholder': 'First name *'})
        self.fields['last_name'].widget = forms.TextInput(attrs={
            'placeholder': 'Last name *'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(BaseUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class BaseUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BaseUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial["password"]


class BaseUserRegistrationForm(BaseUserCreationForm):
    accept = forms.BooleanField(initial=False, label=_('I accept rules and conditions.'),
                                error_messages={'required': _('You must accept the rules')})


class BaseAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254, label=_("Username or Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())


class BaseUserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput())

    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(),
                                    )
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput())


class BasePasswordResetForm(authtoolsforms.FriendlyPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(BasePasswordResetForm, self).__init__(*args, **kwargs)


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(),
                                    )
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput())
