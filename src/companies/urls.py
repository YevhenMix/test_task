from django.contrib import admin
from django.urls import path
from .views import CompaniesView, CompanyView, CompanyCreateView, ClientCompanyView

app_name = 'companies'

urlpatterns = [
    path('all/<str:view>', CompaniesView.as_view(), name='all_companies'),
    path('company/<int:company_id>', CompanyView.as_view(), name='one_company'),
    path('company/create', CompanyCreateView.as_view(), name='create_company'),
    path('my_company/', ClientCompanyView.as_view(), name='client_company'),
]
