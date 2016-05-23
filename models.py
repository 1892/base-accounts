from django.core import validators
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from .options.choices import *
from .tools import *

USER_MODEL = settings.AUTH_USER_MODEL


class BaseUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=100, unique=True,
                                help_text=_('Required. 75 characters or fewer. Letters, digits and '
                                            '@/./+/-/_ only.'),
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
                                ])
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=False,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # activation confirm
    activation_key = models.CharField(max_length=250, blank=True, null=True, unique=True)
    expiration_date = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "{} {}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    class Meta:
        abstract = True


class BaseProfile(models.Model):
    user = models.OneToOneField(USER_MODEL)
    birthday = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(blank=True, null=True, upload_to=get_pic_file_name)
    social_picture = models.CharField(max_length=255, blank=True, null=True)
    social_id = models.CharField(max_length=125, blank=True, null=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)

    def __str__(self):
        return self.user.username

    @property
    def get_profile_picture(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        elif self.social_picture:
            return self.social_picture
        else:
            return '#'

    class Meta:
        abstract = True
