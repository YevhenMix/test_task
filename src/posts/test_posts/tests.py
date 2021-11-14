import logging

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from companies.serializers import CompanySerializer
from posts.models import Post
from posts.serializers import PostsSerializer, PostSerializer
from users.models import User
from companies.models import Company
from users.tests_users.conftest import init_login_super_user, init_login_simple_user


class PostsAPITestCase(APITestCase):
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

        self.simple_user2 = User.objects.create(
            email='simple2@email.com',
            password='testpassword',
            first_name='Simple2',
            last_name='User2',
            user_type='client',
            company_id=self.company_1,
            is_super_admin=False
        )
        self.simple_user2.set_password(self.simple_user2.password)
        self.simple_user2.save()

        self.post_1 = Post.objects.create(
            title='New Title',
            user_id=self.simple_user,
            text='Text text text text',
            topic='news'
        )

        self.post_2 = Post.objects.create(
            title='New Title 2',
            user_id=self.simple_user,
            text='Text text text text',
            topic='test'
        )

        self.post_3 = Post.objects.create(
            title='New Title 3',
            user_id=self.simple_user2,
            text='Text text text text',
            topic='top'
        )


    def test_negative_posts_lst_unauthorized(self):
        url = reverse('posts:all_posts')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @init_login_simple_user
    def test_negative_posts_lst_wrong_permission(self):
        url = reverse('posts:all_posts')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_super_user
    def test_posts_lst(self):
        posts = Post.objects.select_related('user_id').all()
        expected_response = PostsSerializer(posts, many=True)

        url = reverse('posts:all_posts')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response.data)

    def test_negative_get_post_unauthorized(self):
        url = reverse('posts:one_post', args=(self.post_1.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_get_post_wrong_permission(self):
        self.api_client.login(email="simple2@email.com", password="testpassword")

        url = reverse('users:login')
        data = {
            'password': 'testpassword',
            'email': 'simple2@email.com'
        }
        response = self.client.post(url, data=data)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        url = reverse('posts:one_post', args=(self.post_1.id, ))
        response_post = self.client.get(url)

        self.api_client.logout()

        self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

    @init_login_simple_user
    def test_negative_get_post_wrong_id(self):
        url = reverse('posts:one_post', args=(5000, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_simple_user
    def test_get_post(self):
        post = Post.objects.get(id=self.post_1.id)
        serializer = PostSerializer(post)
        url = reverse('posts:one_post', args=(self.post_1.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @init_login_simple_user
    def test_negative_update_post_wrong_id(self):
        url = reverse('posts:one_post', args=(5000, ))

        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_simple_user
    def test_update_post(self):
        post = Post.objects.get(id=self.post_1.id)

        url = reverse('posts:one_post', args=(self.post_1.id, ))
        data = {
            'topic': 'updated'
        }

        response = self.client.patch(url, data=data)
        updated_post = Post.objects.get(id=self.post_1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(updated_post.topic, post.topic)

    @init_login_simple_user
    def test_negative_delete_post_wrong_id(self):
        url = reverse('posts:one_post', args=(5000, ))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @init_login_simple_user
    def test_update_post(self):
        post = Post.objects.filter(id=self.post_1.id)

        url = reverse('posts:one_post', args=(self.post_1.id, ))

        response = self.client.delete(url)
        deleted_post = Post.objects.filter(id=self.post_1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(deleted_post, post)

    @init_login_simple_user
    def test_negative_create_post_wrong_field(self):
        url = reverse('posts:create_post')
        data = {
            'title': 'NEW TITLE',
            'user_id': self.simple_user2.id,
            'text': 'TEST TEXT TEST TEXT',
            'topic': 'new_one',
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @init_login_simple_user
    def test_create_post(self):
        url = reverse('posts:create_post')
        data = {
            'title': 'NEW TITLE',
            'user_id': self.simple_user.id,
            'text': 'TEST TEXT TEST TEXT',
            'topic': 'new_one',
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])

    @init_login_super_user
    def test_create_post_by_admin(self):
        url = reverse('posts:create_post')
        data = {
            'title': 'NEW TITLE',
            'user_id': self.simple_user.id,
            'text': 'TEST TEXT TEST TEXT',
            'topic': 'new_one',
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])

    # @init_login_simple_user
    # def test_negative_bulk_update_posts_by_client_wrong_permission(self):
    #     url = reverse('posts:bulk_update_post')
    #     post_1 = Post.objects.get(id=self.post_1.id)
    #     post_2 = Post.objects.get(id=self.post_3.id)
    #     data = {
    #         'posts_to_update': [{'id': self.post_1.id, 'title': 'Updated Title'}, {'id': self.post_3.id, 'title': 'Updated title 2'}]
    #     }
    #
    #     response = self.client.patch(url, data=data)
    #     updated_post_1 = Post.objects.get(id=self.post_1.id)
    #     updated_post_2 = Post.objects.get(id=self.post_3.id)
    #
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #     self.assertEqual(updated_post_1.title, post_1.title)
    #     self.assertEqual(updated_post_2.title, post_2.title)
    #
    # @init_login_super_user
    # def test_bulk_update_posts_by_admin(self):
    #     url = reverse('posts:bulk_update_post')
    #     post_1 = Post.objects.get(id=self.post_1.id)
    #     post_2 = Post.objects.get(id=self.post_2.id)
    #     expected_message = 'Successfully update posts'
    #     data = {
    #         'posts_to_update': [{'id': self.post_1.id, 'title': 'Updated Title'}, {'id': self.post_2.id, 'title': 'Updated title 2', 'topic': 'new_one'}]
    #     }
    #
    #     response = self.client.patch(url, data=data)
    #     updated_post_1 = Post.objects.get(id=self.post_1.id)
    #     updated_post_2 = Post.objects.get(id=self.post_2.id)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['message'], expected_message)
    #     self.assertNotEqual(updated_post_1.title, post_1.title)
    #     self.assertNotEqual(updated_post_2.title, post_2.title)
    #     self.assertNotEqual(updated_post_2.topic, post_2.topic)
