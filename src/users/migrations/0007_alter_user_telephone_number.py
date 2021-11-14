# Generated by Django 3.2.9 on 2021-11-09 16:24

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_rename_is_admin_user_is_super_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='telephone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region='UA'),
        ),
    ]