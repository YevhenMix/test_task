# Generated by Django 3.2.9 on 2021-11-11 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('super_admin', 'super_admin'), ('client', 'client'), ('admin', 'admin')], default='client', max_length=12, verbose_name='User Type'),
        ),
    ]