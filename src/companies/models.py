from django.db import models


class Company(models.Model):
    name = models.CharField('Company Name', max_length=50, null=False, blank=False)
    url = models.URLField('Link on company page', null=False, blank=True)
    address = models.CharField('Company Address', max_length=200, null=False, blank=True)
    date_created = models.DateField('Foundation Date', null=False, blank=False)
    logo = models.FileField(upload_to='media/companies_logo', null=True, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-date_created']
