from django.urls import reverse


def init_login_super_user(func):
    def inner(*args, **kwargs):
        user = args[0]
        user.api_client.login(email="super_admin@email.com", password="testpassword")

        url = reverse('users:login')
        data = {
            'password': 'testpassword',
            'email': 'super_admin@email.com'
        }

        response = user.client.post(url, data=data)
        user.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        func(*args, **kwargs)

        user.api_client.logout()
    return inner


def init_login_admin(func):
    def inner(*args, **kwargs):
        user = args[0]
        user.api_client.login(email="admin@email.com", password="testpassword")

        url = reverse('users:login')
        data = {
            'password': 'testpassword',
            'email': 'admin@email.com'
        }

        response = user.client.post(url, data=data)
        user.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        func(*args, **kwargs)

        user.api_client.logout()
    return inner


def init_login_simple_user(func):
    def inner(*args, **kwargs):
        user = args[0]
        user.api_client.login(email="simple@email.com", password="testpassword")

        url = reverse('users:login')
        data = {
            'password': 'testpassword',
            'email': 'simple@email.com'
        }

        response = user.client.post(url, data=data)
        user.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        func(*args, **kwargs)

        user.api_client.logout()
    return inner
