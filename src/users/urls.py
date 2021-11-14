from django.contrib import admin
from django.urls import path, include
from .views import UsersView, UserCreateView, UserView, AccountView


app_name = 'users'

urlpatterns = [
    path('all/', UsersView.as_view(), name='all_users'),
    path('user/create', UserCreateView.as_view(), name='create_user'),
    path('user/<int:user_id>', UserView.as_view(), name='one_user'),
    path('user/account', AccountView.as_view(), name='account'),
    path('user/', include('djoser.urls.authtoken')),
]
