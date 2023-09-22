from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from datetime import datetime


class ShortURL(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_url = models.URLField()
    short_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=50, blank=True)
    custom_note = models.TextField(blank=True)
    accurate_location_tracking = models.BooleanField(default=False)


    def get_absolute_url(self):
        return f"/{self.short_code}/"

    def __str__(self):
        return self.short_code



class UserLocation(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shortlink_userlocations', null=True, blank=True)
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
        return f"{self.short_url.short_code} - {self.ip_address} - {self.date} - {self.time}"

    def save(self, *args, **kwargs):
        # Check if the user is authenticated or anonymous
        if isinstance(self.author, AnonymousUser):
            self.author = None  # Set author to None for anonymous users
        # set the date to the current time and date
        self.date = datetime.now()

        # format the date using the strftime method
        datetamp_str = self.date.strftime("%d/%m/%Y")

        # save the model instance
        super().save(*args, **kwargs)
        