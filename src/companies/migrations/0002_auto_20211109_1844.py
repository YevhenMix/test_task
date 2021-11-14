# Generated by Django 3.2.9 on 2021-11-09 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.FileField(null=True, upload_to='media/companies_logo'),
        ),
        migrations.AlterField(
            model_name='company',
            name='url',
            field=models.URLField(blank=True, verbose_name='Link on company page'),
        ),
    ]