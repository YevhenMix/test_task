from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User
from companies.models import Company
from .conftest import init_login_super_user, init_login_simple_user, init_login_admin
from ..serializers import UserListSerializers, UserSerializer, CreateUserSerializer


class UsersAPITestCase(APITestCase):
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

        self.admin = User.objects.create(
            email='admin@email.com',
            password='testpassword',
            first_name='Admin',
            last_name='User',
            user_type='admin',
            company_id=self.company_1,
            is_super_admin=False
        )
        self.admin.set_password(self.admin.password)
        self.admin.save()

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

    def test_user_login(self):
        self.api_client.login(email="super_admin@email.com", password="testpassword")

        url = reverse('users:login')
        data = {
            'password': 'testpassword',
            'email': 'super_admin@email.com'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'auth_token')

    def test_negative_user_lst_view_unauthorized(self):
        url = reverse('users:all_users')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @init_login_simple_user
    def test_negative_user_lst_view_wrong_permission(self):
        url = reverse('users:all_users')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_super_user
    def test_user_lst_view(self):
        users = User.objects.select_related('company_id').all()
        expected_data = UserListSerializers.get_response_with_company_info(users)

        url = reverse('users:all_users')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_negative_user_view_unauthorized(self):
        url = reverse('users:one_user', args=(self.simple_user.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @init_login_simple_user
    def test_negative_user_view_wrong_permission(self):
        url = reverse('users:one_user', args=(self.simple_user.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_super_user
    def test_negative_user_view_wrong_user(self):
        url = reverse('users:one_user', args=(50000, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_super_user
    def test_user_view(self):
        user = User.objects.get(id=self.simple_user.id)
        serializer = UserSerializer(user)

        url = reverse('users:one_user', args=(self.simple_user.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @init_login_super_user
    def test_negative_update_user_view_wrong_user(self):
        url = reverse('users:one_user', args=(50000, ))

        data = {
            'first_name': 'Updated Name'
        }

        response = self.client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_super_user
    def test_negative_update_user_view_wrong_field(self):
        url = reverse('users:one_user', args=(self.simple_user.id,))
        data = {
            'telephone_number': '380'
        }
        response = self.client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @init_login_super_user
    def test_update_user_view(self):
        user = User.objects.get(id=self.simple_user.id)

        url = reverse('users:one_user', args=(self.simple_user.id,))
        data = {
            'first_name': 'Updated Name'
        }
        response = self.client.patch(url, data=data)
        updated_user = User.objects.get(id=self.simple_user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(user.first_name, updated_user.first_name)

    @init_login_super_user
    def test_negative_delete_user_view_wrong_user(self):
        url = reverse('users:one_user', args=(50000, ))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_super_user
    def test_soft_delete_user_view(self):
        user = User.objects.get(id=self.simple_user.id)
        url = reverse('users:one_user', args=(self.simple_user.id,)) + '?soft_delete=true'
        response = self.client.delete(url)
        deleted_user = User.objects.get(id=self.simple_user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(deleted_user.is_deleted, user.is_deleted)

    @init_login_super_user
    def test_permanent_delete_user_view(self):
        user = User.objects.filter(id=self.simple_user.id)

        url = reverse('users:one_user', args=(self.simple_user.id,))

        response = self.client.patch(url)
        deleted_user = User.objects.filter(id=self.simple_user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(deleted_user, user)

    @init_login_simple_user
    def test_negative_create_user_view_wrong_permission(self):
        url = reverse('users:create_user')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_admin
    def test_negative_create_user_view_by_admin_wrong_user_type(self):
        url = reverse('users:create_user')
        data = {
            'email': 'new@email.com',
            'password': 'newpass',
            'first_name': 'New User',
            'last_name': 'New Last',
            'user_type': 'super_admin',
            'company_id': self.company_1,
            'telephone_number': '+380964225645',
            'is_super_admin': True
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @init_login_admin
    def test_create_user_view_by_admin(self):
        url = reverse('users:create_user')
        data = {
            'email': 'new@email.com',
            'password': 'newpassword',
            'first_name': 'New User',
            'last_name': 'New Last',
            'user_type': 'client',
            'company_id': self.company_1.id,
            'telephone_number': '+380964225645',
        }

        response = self.client.post(url, data=data)
        user = User.objects.get(email='new@email.com')
        serializer = CreateUserSerializer(user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data['email'], data['email'])

    @init_login_super_user
    def test_create_user_view_by_super_admin(self):
        url = reverse('users:create_user')
        data = {
            'email': 'new@email.com',
            'password': 'newpassword',
            'first_name': 'New User',
            'last_name': 'New Last',
            'user_type': 'super_admin',
            'company_id': self.company_1.id,
            'telephone_number': '+380964225645',
            'is_super_admin': True
        }

        response = self.client.post(url, data=data)
        user = User.objects.get(email='new@email.com')
        serializer = CreateUserSerializer(user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data['email'], data['email'])
