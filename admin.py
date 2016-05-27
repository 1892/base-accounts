from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


class BaseUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', "first_name", "last_name", 'email', 'password1', 'password2'),
        }),
    )
    # The forms to add and change user instances
    form = BaseUserChangeForm
    add_form = BaseUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'username',)
    list_filter = ('is_active', 'is_staff', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)


class BaseProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user', 'birthday', 'profile_picture', 'gender')}),
        (_('Social informations'), {'fields': ('social_picture', 'social_id')}),
    )
    list_display = ('user', 'gender', 'social_id',)
    list_filter = ('gender', )
    search_fields = ('social_id', 'birthday')

