# Generated by Django 5.2.1 on 2025-05-12 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportscomplex', '0006_usertyperate_alter_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertyperate',
            name='registration_fee',
            field=models.PositiveIntegerField(default=2000, help_text='One-time registration fee'),
        ),
    ]
