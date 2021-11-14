from django.contrib import admin
from .models import User


@admin.register(User)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'company_id', 'telephone_number', 'id')
