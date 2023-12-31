# Generated by Django 4.1.4 on 2023-04-29 11:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactFormData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VisitCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_count', models.IntegerField(default=0)),
                ('today_total', models.IntegerField(default=0)),
                ('monthly_total', models.IntegerField(default=0)),
                ('yearly_total', models.IntegerField(default=0)),
                ('last_visit_date', models.DateField(default=datetime.date(2023, 4, 29))),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('continent', models.CharField(blank=True, max_length=64, null=True)),
                ('country', models.CharField(blank=True, max_length=64, null=True)),
                ('region', models.CharField(blank=True, max_length=64, null=True)),
                ('region_name', models.CharField(blank=True, max_length=64, null=True)),
                ('city', models.CharField(blank=True, max_length=64, null=True)),
                ('district', models.CharField(blank=True, max_length=64, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=64, null=True)),
                ('timezone', models.CharField(blank=True, max_length=64, null=True)),
                ('isp', models.CharField(blank=True, max_length=64, null=True)),
                ('org', models.CharField(blank=True, max_length=64, null=True)),
                ('as_number', models.CharField(blank=True, max_length=64, null=True)),
                ('as_name', models.CharField(blank=True, max_length=64, null=True)),
                ('mobile', models.BooleanField(blank=True, null=True)),
                ('proxy', models.BooleanField(blank=True, null=True)),
                ('hosting', models.BooleanField(blank=True, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=64, null=True)),
                ('map_link', models.CharField(blank=True, max_length=256, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('user_agent', models.CharField(blank=True, max_length=256, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TokenSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, unique=True)),
                ('chat_id', models.CharField(default=0, max_length=64)),
                ('link', models.CharField(blank=True, max_length=256, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResetCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
