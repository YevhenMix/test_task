from django.contrib import admin
from django.urls import path, re_path

from .views import PostsView, PostView, PostCreateView, PostBulkUpdateView, CompanyPostsView

app_name = 'posts'

urlpatterns = [
    path('all/', PostsView.as_view(), name='all_posts'),
    path('company', CompanyPostsView.as_view(), name='one_company_posts'),
    path('post/create', PostCreateView.as_view(), name='create_post'),
    path('bulk_update/', PostBulkUpdateView.as_view(), name='bulk_update_post'),
    path('post/<int:post_id>', PostView.as_view(), name='one_post'),
]
