from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import datetime as dt
from utils.hasher import HashHelper
import uuid
from .exceptions import EmailAlreadyUsed, UserAlreadyInvited


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # CRM Data
    picture_url = models.TextField(_('picture URL'), max_length=500, null=True, blank=True)
    
    # Reset Password
    reset_token = models.TextField(max_length=200, null=True, blank=True)
    update_token_at = models.DateTimeField(default=None, null=True, blank=True)
    ask_reset_at = models.DateTimeField(default=dt.now, null=True, blank=True)
    
    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)
    
    class Meta:
        ordering = ('user',)
    
    @classmethod
    def create(cls, email, first_name, last_name, picture_url):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(username=email,
                                            email=email,
                                            password=User.objects.make_random_password(),
                                            first_name=first_name,
                                            last_name=last_name)
            user.is_active = False
            user.save()
        
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = cls(user=user)
            profile.picture_url = picture_url
            profile.save()
        if not user.is_active:
            profile.reset_token = Profile.get_new_reset_token()
            profile.save()
            return profile
        raise EmailAlreadyUsed
    
    def send_email(self, subject, message):
        """
        Send Async Email to the user
        :param subject: Subject of the email
        :param message: Email Content
        :return: Nothing
        """
        import threading
        thr = threading.Thread(target=Profile._send_email,
                               kwargs=dict(message=message,
                                           subject=subject,
                                           receiver_name=self.user.get_full_name(),
                                           receiver_email=self.user.email
                                           ))
        thr.start()
    
    @staticmethod
    def _send_email(subject, message, receiver_name, receiver_email):
        """
        Send Email method
        :param subject: Subject of the email
        :param message: Email Content
        :param receiver_name: Name of the receiver
        :param receiver_email: Email of the receiver
        :return: Nothing
        """
        from utils.mailer import EmailHelper
        EmailHelper.send_email(message=message,
                               subject=subject,
                               receiver_name=receiver_name,
                               receiver_email=receiver_email)
        
    @staticmethod
    def get_new_reset_token():
        """
        Generate a new reset Token
        :return: String
        """
        return str(uuid.uuid4())

    @classmethod
    def search_members(cls, search_string):
        from django.db.models import Q
        profiles = cls.objects.filter(Q(user__email__contains=search_string) |
                                      Q(user__first_name__contains=search_string) |
                                      Q(user__last_name__contains=search_string))
        return profiles

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.get(user__email=email)

    @classmethod
    def get_by_id(cls, profile_id):
        return cls.objects.get(id=profile_id)


class Invitation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    sender_email = models.EmailField(max_length=254, verbose_name='email address')
    sender_first_name = models.TextField(max_length=200, null=False, blank=False, default='--')
    sender_last_name = models.TextField(max_length=200, null=False, blank=False, default='--')

    receiver_email = models.EmailField(max_length=254, verbose_name='email address')
    receiver_first_name = models.TextField(max_length=200, null=False, blank=False, default='--')
    receiver_last_name = models.TextField(max_length=200, null=False, blank=False, default='--')

    sender_verified = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, user, sender_email, sender_first_name, sender_last_name, receiver_email, receiver_first_name, receiver_last_name, sender_verified):
        try:
            Invitation.objects.get(email=HashHelper.md5_hash(receiver_email))
            raise UserAlreadyInvited
        except Invitation.DoesNotExist:
            pass
        try:
            user = User.objects.get(email=receiver_email)
            raise EmailAlreadyUsed
        except User.DoesNotExist:
            pass

        try:
            # ToDo Profile could be null
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = None
            pass

        invitation = cls(profile=profile,
                         sender_email=sender_email,
                         sender_first_name=sender_first_name,
                         sender_last_name=sender_last_name,
                         receiver_first_name=receiver_first_name,
                         receiver_last_name=receiver_last_name,
                         receiver_email=receiver_email,
                         sender_verified=sender_verified)
        invitation.save()
        return invitation


class Feedback(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    message_text = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=dt.now)

    class Meta:
        ordering = ('created_at', 'title',)

    @classmethod
    def create(cls, user, title, message_text):
        model = cls(cls, user, title, message_text)
        return model

    def __str__(self):
        return self.message_text
