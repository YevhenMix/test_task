# Generated by Django 3.2.9 on 2021-11-10 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.FileField(null=True, upload_to='media/user_avatar'),
        ),
    ]
