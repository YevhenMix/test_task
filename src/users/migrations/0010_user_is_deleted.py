# Generated by Django 3.2.9 on 2021-11-10 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]