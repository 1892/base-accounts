import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic import *
from authtools import views as authtools
from django.contrib.auth import get_user_model
from django import forms as django_forms
from .models import *
from .forms import *
import logging

User = get_user_model()
# Get an instance of a logger
logr = logging.getLogger(__name__)


# User registration
class UserRegistration(CreateView):
    model = User
    form_class = BaseUserRegistrationForm
    template_name = "base_accounts/registration.html"
    success_url = reverse_lazy("base_accounts:email_confirm")
    home_page = '/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.home_page)
        return super(UserRegistration, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session['email'] = form.cleaned_data.get('email')
        return super(UserRegistration, self).form_valid(form)


class UserRegistrationConfirmEmail(TemplateView):
    template_name = "base_accounts/registration-confirm-email.html"
    home_page = '/'

    def get_context_data(self, **kwargs):
        context = super(UserRegistrationConfirmEmail, self).get_context_data(**kwargs)
        context['email'] = self.request.session['email']
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.home_page)
        return super(UserRegistrationConfirmEmail, self).get(request, *args, **kwargs)


class EmailConfirm(View):
    success_url = '/'

    def get(self, request):
        try:
            activation_key = django_forms.CharField().clean(request.GET.get("activation"))
            confirm_user = User.objects.get(activation_key=activation_key)
            if confirm_user.is_active:
                return HttpResponseForbidden()

            if confirm_user.expiration_date > timezone.now():
                confirm_user.is_active = True
                confirm_user.save()
                confirm_user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, confirm_user)
                return redirect(self.success_url)
            else:
                raise ValueError()

        except (User.DoesNotExist, ValueError, django_forms.ValidationError):
            return HttpResponseBadRequest()


class BaseUserLoginView(FormView):
    form_class = BaseAuthenticationForm
    template_name = 'base_accounts/login.html'
    success_url = reverse_lazy("base_accounts:home")
    home_page = reverse_lazy("base_accounts:home")
    logout_url = reverse_lazy("base_accounts:logout")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.home_page)
        return super(BaseUserLoginView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get('next', None)
        if next_url:
            if next_url == self.logout_url:
                return self.home_page
            return next_url
        else:
            return self.home_page

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(email=username, password=password)

        if user.is_active:
            login(self.request, user)
            if self.request.session.get('email', None):
                del self.request.session['email']
            return super(BaseUserLoginView, self).form_valid(form)
        else:
            return self.form_invalid(form)


class BaseUserLogOutView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("base_accounts:login")
    login_url = reverse_lazy("base_accounts:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(BaseUserLogOutView, self).get(request, *args, **kwargs)


class BaseUserPasswordChangeView(authtools.PasswordChangeView):
    form_class = BaseUserPasswordChangeForm
    template_name = 'base_accounts/password_change_form.html'
    success_url = reverse_lazy("base_accounts:home")
    login_url = reverse_lazy("base_accounts:password_change_done")

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please relogin")
        return super(BaseUserPasswordChangeView, self).form_valid(form)


class BaseUserPasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'base_accounts/password_change_done.html'


class BaseUserPasswordResetView(authtools.PasswordResetView):
    form_class = BasePasswordResetForm
    domain_override = settings.HOST
    template_name = 'base_accounts/password-reset.html'
    success_url = reverse_lazy('base_accounts:password-reset-done')
    home_page = '/'
    subject_template_name = 'emails/password-reset-subject.txt'
    email_template_name = 'emails/user-password-reset-email.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.home_page)
        return super(BaseUserPasswordResetView, self).get(request, *args, **kwargs)


class BaseUserPasswordResetDoneView(authtools.PasswordResetDoneView):
    template_name = 'base_accounts/password-reset-done.html'
    home_page = '/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.home_page)
        return super(BaseUserPasswordResetDoneView, self).get(request, *args, **kwargs)


class UserPasswordResetConfirmView(authtools.PasswordResetConfirmAndLoginView):
    template_name = 'base_accounts/password-reset-confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("base_accounts:home")
