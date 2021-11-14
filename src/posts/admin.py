from django.contrib import admin
from .models import Post


@admin.register(Post)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_id', 'topic', 'id')
