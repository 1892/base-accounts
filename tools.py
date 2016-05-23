import hashlib
import datetime
from time import time
import random
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage


def get_pic_file_name(instance, filename):
    """
    Sets default destination of user`s avatar pic path and changes filename
    to `time + filename` to prevent duplicate file names.
    """
    return "accounts/avatar/%s_%s" % (str(time()).replace('.', '_'), filename)


# Email confirmation
class EmailActivation:
    success_url = '/'

    def __init__(self, user):
        self.user = user

    def send_activation(self):
        salt = hashlib.sha1(str(random.random()).encode("utf-8")).hexdigest()[:10]
        key = hashlib.sha256(str(self.user.email + salt).encode("utf-8")).hexdigest()
        self.user.activation_key = key
        self.user.expiration_date = timezone.now() + datetime.timedelta(days=1)
        self.user.save()
        print(settings.HOST, self.success_url)
        subject = "Confirmation of registration"
        txt = """Thank you for registration,
            please click the following link in order to confirm your registration:
            {link}?activation={key}
            """.format(link="".join([settings.HOST, str(self.success_url)]), key=key)
        to = [self.user.email]
        from_email = settings.EMAIL_HOST_USER
        EmailMessage(subject, txt, to=to, from_email=from_email).send()
