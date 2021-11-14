from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from companies.serializers import CompanySerializer
from users.models import User
from companies.models import Company
from users.tests_users.conftest import init_login_super_user, init_login_simple_user


class CompanyAPITestCase(APITestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = APIClient()

    def setUp(self):
        self.company_1 = Company.objects.create(
            name='name_1',
            url='https://www.youtube.com/',
            address='test address',
            date_created='2001-10-21',
        )

        self.super_admin = User.objects.create(
            email='super_admin@email.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            user_type='super_admin',
            company_id=self.company_1,
            is_super_admin=True
        )
        self.super_admin.set_password(self.super_admin.password)
        self.super_admin.save()

        self.simple_user = User.objects.create(
            email='simple@email.com',
            password='testpassword',
            first_name='Simple',
            last_name='User',
            user_type='client',
            company_id=self.company_1,
            is_super_admin=False
        )
        self.simple_user.set_password(self.simple_user.password)
        self.simple_user.save()

    @init_login_simple_user
    def test_negative_companies_lst_wrong_permission(self):
        url = reverse('companies:all_companies', args=('partial', ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_super_user
    def test_negative_companies_lst_wrong_view_type(self):
        expected_message = 'View option must be partial or full not all'
        url = reverse('companies:all_companies', args=('all', ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], expected_message)

    @init_login_super_user
    def test_companies_lst_partial(self):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        url = reverse('companies:all_companies', args=('partial', ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @init_login_super_user
    def test_companies_lst_full(self):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        expected_response = CompanySerializer.generate_full_result(serializer.data)
        url = reverse('companies:all_companies', args=('full', ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @init_login_super_user
    def test_negative_get_company_wrong_id(self):
        url = reverse('companies:one_company', args=(5000,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_super_user
    def test_get_company(self):
        company = Company.objects.get(id=self.company_1.id)
        serializer = CompanySerializer(company)
        url = reverse('companies:one_company', args=(self.company_1.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @init_login_super_user
    def test_negative_update_company_wrong_id(self):
        url = reverse('companies:one_company', args=(5000,))

        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_super_user
    def test_negative_update_company_wrong_field(self):
        url = reverse('companies:one_company', args=(self.company_1.id,))
        data = {
            'date_created': 'error'
        }

        response = self.client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @init_login_super_user
    def test_update_company(self):
        company = Company.objects.get(id=self.company_1.id)

        url = reverse('companies:one_company', args=(self.company_1.id,))
        data = {
            'address': 'mew address'
        }

        response = self.client.patch(url, data=data)
        updated_company = Company.objects.get(id=self.company_1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(updated_company.address, company.address)

    def test_negative_create_company_unauthorized(self):
        url = reverse('companies:create_company')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @init_login_simple_user
    def test_negative_create_company_wrong_permission(self):
        url = reverse('companies:create_company')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_super_user
    def test_negative_create_company_wrong_field(self):
        url = reverse('companies:create_company')
        data = {
            'name': 'Name',
            'url': 'error',
            'address': 'Some address',
            'date_created': '1985-10-12',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @init_login_super_user
    def test_create_company(self):
        url = reverse('companies:create_company')
        data = {
            'name': 'New Name',
            'url': 'https://www.youtube.com/',
            'address': 'Some address',
            'date_created': '1985-10-12',
        }

        response = self.client.post(url, data=data)
        created_company = Company.objects.get(name=data['name'])
        serializer = CompanySerializer(created_company)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data['name'], data['name'])
