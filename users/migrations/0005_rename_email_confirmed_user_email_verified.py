# Generated by Django 4.1.2 on 2022-11-16 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_email_confirmed_user_email_secret'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='email_confirmed',
            new_name='email_verified',
        ),
    ]
