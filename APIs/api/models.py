from itertools import combinations
from unittest import result
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# from django.conf import settings
# from django.db.models.signals import post_save,post_delete
from django.utils import timezone

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
import smtplib
import os
from uuid import uuid4
from functools import partial


def path_and_rename(path):
    return partial(wrapper, path=path)


def wrapper(instance, filename, path):
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        # filename = '{}.{}'.format(instance.pk, ext)
        filename = "{}.{}".format(uuid4().hex, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(path, filename)


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    # email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    # send_mail(
    #     # title:
    #     "Password Reset for {title}".format(title="MyFight"),
    #     # message:
    #     email_plaintext_message,
    #     # from:
    #     "mbilal.pg@gmail.com",
    #     # to:
    #     [reset_password_token.user.email]
    # )
    print("Email sent!")
    gmail_user = "AKIATSYGAHUONRNUSS44"
    gmail_app_password = "BB1iie6bDD/GhSOYLbc/AjVJHPZPe8fWu2Jln56x6ruF"
    sent_from = "mbilal.pg@gmail.com"
    sent_to = ["mbilal.pg@gmail.com", "mbilal.pg@gmail.com"]
    sent_subject = "Hello World"
    sent_body = "Its me World"
    email_text = """\ From: %s
                    To: %s
                    Subject: %s
                    %s
                    """ % (
        sent_from,
        ", ".join(sent_to),
        sent_subject,
        sent_body,
    )

    try:
        server = smtplib.SMTP_SSL("email-smtp.us-east-1.amazonaws.com", 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text.encode("utf-8"))
        server.close()
        print(email_text)
        print("Email sent!")
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save()
        return user


class User(AbstractBaseUser):
    objects = UserManager()
    id = models.AutoField(primary_key=True)
    phone_no = models.CharField(max_length=200, blank=True, null=True, default="")
    gender = models.CharField(max_length=200, default="Unknown", blank=True)
    photo = models.FileField(
        default="avatar.png", blank=True, upload_to=path_and_rename("users/")
    )
    mailing_address = models.CharField(max_length=200, blank=True)
    device = models.CharField(max_length=200, blank=True)
    device_id = models.CharField(max_length=200, blank=True)
    firebase_token = models.CharField(max_length=200, blank=True)
    status = models.BooleanField(default=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=120, default="", blank=False)
    username = models.CharField(unique=True, max_length=120, default="", blank=False)
    facebook_id = models.CharField(max_length=250, default=0, blank=False)
    belt_type = models.CharField(max_length=250, default="white", blank=False)
    tribe_id = models.IntegerField(default=0, blank=True)

    is_active = models.BooleanField("active", default=True)
    is_admin = models.BooleanField("admin", default=False)
    is_fighter = models.BooleanField("fighter", default=False)
    is_online = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    ordering = ("created",)

    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def __unicode__(self):
        return self.email


class Fighters(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150, blank=False)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class FighterVideos(models.Model):
    id = models.AutoField(primary_key=True)
    # fighter_id = models.IntegerField(default=0,blank=True)
    fighter = models.ForeignKey(User, default=0, blank=True, on_delete=models.CASCADE)
    belt = models.CharField(max_length=150, blank=False)
    # type = models.CharField(max_length=150, blank=False)
    title = models.CharField(max_length=150, default=0, blank=False)
    cam_angle_1 = models.CharField(max_length=250, default=0, blank=False)
    cam_angle_2 = models.CharField(max_length=250, default=0, blank=False)
    cam_angle_3 = models.CharField(max_length=250, default=0, blank=False)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class PlayerVideos(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ForeignKey(User, default=0, blank=True, on_delete=models.CASCADE)
    fighter_video = models.ForeignKey(
        FighterVideos, default=0, blank=True, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250, blank=False)
    file_name = models.FileField(
        blank=False, upload_to=path_and_rename("player_videos/")
    )
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class PlayerActionsResult(models.Model):
    id = models.AutoField(primary_key=True)
    # player = models.ForeignKey(User,default=0,blank=True,on_delete=models.CASCADE)
    player_id = models.IntegerField(default=0, blank=True)
    # fighter_video = models.ForeignKey(FighterVideos,default=0,blank=True,on_delete=models.CASCADE)
    fighter_video_id = models.IntegerField(default=0, blank=True)
    # player_video = models.ForeignKey(PlayerVideos,default=0,blank=True,on_delete=models.CASCADE)
    player_video_id = models.IntegerField(default=0, blank=True)
    result = models.CharField(max_length=255, blank=True, default=0)
    result_details = models.CharField(max_length=500, default=0)
    # json_file = models.FileField(blank=False)
    json_file = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class FightStrategy(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ForeignKey(User, default=0, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=False)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class FightStrategyVideo(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ForeignKey(User, default=0, blank=True, on_delete=models.CASCADE)
    # player_video = models.ForeignKey(
    #     PlayerVideos, default=0, blank=True, on_delete=models.CASCADE
    # )
    player_video_id = models.IntegerField(default=0, blank=True, null=True)
    fight_strategy = models.ForeignKey(
        FightStrategy, default=0, blank=True, on_delete=models.CASCADE
    )
    combination = models.CharField(max_length=150, default=1, blank=False)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=0, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class Tribes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, blank=False)
    user = models.ForeignKey(User, default=1, blank=True, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(default=1, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)


class Friends(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    status = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)
    created_by = models.IntegerField(default=1, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=1, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        unique_together = ("user", "friend")


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    # json_field = models.JSONField(default={})


# class Profile(models.Model):
#     GENDER = (
#         ('M', 'Homme'),
#         ('F', 'Femme'),
#     )
#
#     user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=120, blank=False)
#     last_name = models.CharField(max_length=120, blank=False)
#     gender = models.CharField(max_length=1, choices=GENDER)
#     zip_code = models.CharField(max_length=5, blank=False)
#
#     def __unicode__(self):
#         return u'Profile of user: {0}'.format(self.user.email)
#
#
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
# post_save.connect(create_profile, sender=User)
#
#
# def delete_user(sender, instance=None, **kwargs):
#     try:
#         instance.user
#     except User.DoesNotExist:
#         pass
#     else:
#         instance.user.delete()
# post_delete.connect(delete_user, sender=Profile)
