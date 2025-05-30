# Generated by Django 5.1.5 on 2025-05-05 19:57

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility_name', models.CharField(choices=[('swimming', 'Swimming'), ('gym', 'Gym'), ('bowling', 'Bowling'), ('badminton', 'Badminton')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(blank=True, max_length=11)),
                ('type', models.CharField(choices=[('faculty', 'Faculty'), ('student', 'Student'), ('alumni', 'Alumni'), ('staff', 'Staff')], max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.PositiveIntegerField()),
                ('date_of_payment', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField(auto_now_add=True)),
                ('method', models.CharField(choices=[('Online', 'Online'), ('Cash', 'Cash')], max_length=6)),
                ('payment_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed')], default='pending', max_length=10)),
                ('fixed_amount', models.PositiveIntegerField()),
                ('membership_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_users', to=settings.AUTH_USER_MODEL)),
                ('membership_payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_payments', to='sportscomplex.payment')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('timing', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed')], default='pending', max_length=10)),
                ('is_walkin', models.BooleanField()),
                ('booking_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_users', to=settings.AUTH_USER_MODEL)),
                ('booking_facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='sportscomplex.facility')),
                ('booking_payment', models.ForeignKey(default='Cash', on_delete=django.db.models.deletion.CASCADE, related_name='booking_payments', to='sportscomplex.payment')),
            ],
        ),
        migrations.CreateModel(
            name='StaffFacilityAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_date', models.DateField()),
                ('shift', models.CharField(max_length=15)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sportscomplex.facility')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sportscomplex.staff')),
            ],
        ),
        migrations.AddField(
            model_name='staff',
            name='assignment',
            field=models.ManyToManyField(related_name='staff_assignments', through='sportscomplex.StaffFacilityAssignment', to='sportscomplex.facility'),
        ),
    ]
