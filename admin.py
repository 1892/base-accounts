from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


class BaseUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("first_name", "last_name", 'email', 'password1', 'password2'),
        }),
    )
    # The forms to add and change user instances
    form = BaseUserChangeForm
    add_form = BaseUserCreationForm
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
