# Generated by Django 3.2.9 on 2021-11-09 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20211109_1614'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_admin',
            new_name='is_super_admin',
        ),
    ]
