
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.text import slugify
from datetime import datetime,date


class TokenSummary(models.Model):
    token = models.CharField(max_length=64, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=64,default=0)
    link = models.CharField(max_length=256, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def verify_token(self):
        self.is_verified = True
        self.save()

    def is_token_verified(self):
        return self.is_verified

    def __str__(self):
        return f"Author: {self.author}, Chat ID: {self.chat_id}"

@receiver(models.signals.pre_save, sender=TokenSummary)
def generate_link(sender, instance, **kwargs):
    server_address = "http://{{ SERVER_ADDRESS }}"
    token = instance.token
    slug = slugify(token)
    link = f"{server_address}/location/{slug}"
    instance.link = link


class UserLocation(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    continent = models.CharField(max_length=64, null=True, blank=True)
    country = models.CharField(max_length=64, null=True, blank=True)
    region = models.CharField(max_length=64, null=True, blank=True)
    region_name = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    district = models.CharField(max_length=64, null=True, blank=True)
    zip_code = models.CharField(max_length=64, null=True, blank=True)
    timezone = models.CharField(max_length=64, null=True, blank=True)
    isp = models.CharField(max_length=64, null=True, blank=True)
    org = models.CharField(max_length=64, null=True, blank=True)
    as_number = models.CharField(max_length=64, null=True, blank=True)
    as_name = models.CharField(max_length=64, null=True, blank=True)
    mobile = models.BooleanField(null=True, blank=True)
    proxy = models.BooleanField(null=True, blank=True)
    hosting = models.BooleanField(null=True, blank=True)
    ip_address = models.CharField(null=True, blank=True,max_length=64)
    map_link = models.CharField(max_length=256, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    user_agent_browser_family = models.CharField(max_length=256, blank=True, null=True)
    user_agent_browser_version = models.CharField(max_length=256, blank=True, null=True)
    user_agent_os = models.CharField(max_length=256, blank=True, null=True)
    user_agent_device = models.CharField(max_length=256, blank=True, null=True)
    is_mobile = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_pc = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"User: {self.author}"

    def save(self, *args, **kwargs):
        # set the date to the current time and date
        self.date = datetime.now()

        # format the date using the strftime method
        datetamp_str = self.date.strftime("%d/%m/%Y")

        # save the model instance
        super().save(*args, **kwargs)


class VisitCount(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    visit_count = models.IntegerField(default=0)
    today_total = models.IntegerField(default=0)
    monthly_total = models.IntegerField(default=0)
    yearly_total = models.IntegerField(default=0)
    last_visit_date = models.DateField(default=date.today())

    def __str__(self):
        return f"User: {self.author}, Visit Count: {self.visit_count}"

class ContactFormData(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Verification code for user {self.user} - Expires at {self.expires_at}"

class ResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Reset code for user {self.user} - Expires at {self.expires_at}"

