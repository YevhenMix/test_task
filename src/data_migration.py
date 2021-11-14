import os
import sys
import random

sys.path.append('../src')
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_task.settings'

import django

django.setup()

from companies.models import Company
from users.models import User
from posts.models import Post
from django.core.files import File
from faker import Faker
import requests


class DataMigration:

    def __init__(self, number_companies, number_user, number_posts):
        self.faker = Faker()
        # self.images = self.get_images(number_images=number_user+number_companies)
        self.companies = self.generate_companies(number_companies)
        self.users = self.generate_users(number_user)
        self.posts = self.generate_posts(number_posts)

    def run(self):
        self.insert_companies_into_db()
        self.insert_users_into_db()
        self.insert_posts_into_db()

    def insert_companies_into_db(self):
        print('Start insert companies in db')
        for index, company in enumerate(self.companies):
            with open(f'./images_for_data_migration/{index}.jpg', 'rb') as file:
                company['logo'] = File(file)
                Company.objects.create(
                    name=company['name'],
                    url=company['url'],
                    address=company['address'],
                    date_created=company['date_created'],
                    logo=company['logo']
                )
        print('Insert companies in db end')

    def insert_users_into_db(self):
        print('Start insert users in db')
        created_companies = Company.objects.all()
        for index, user in enumerate(self.users):
            with open(f'./images_for_data_migration/{index + 10}.jpg', 'rb') as file:
                user['avatar'] = File(file)
                user = User.objects.create(
                    email=user['email'],
                    password=user['password'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    user_type=user['user_type'],
                    company_id=created_companies[random.randint(0, len(created_companies) - 1)],
                    avatar=user['avatar'],
                    telephone_number=user['telephone_number']
                )
                user.set_password(user.password)
                user.save()
        print('Insert users in db end')

    def insert_posts_into_db(self):
        print('Start insert posts in db')
        created_users = User.objects.all()
        post_lst = []
        for post in self.posts:
            post_lst.append(
                Post(
                    title=post['title'],
                    user_id=created_users[post['user_id'] - 1],
                    text=post['text'],
                    topic=post['topic']
                )
            )

            if len(post_lst) == 1000:
                Post.objects.bulk_create(post_lst, batch_size=1000)
                post_lst = []
        print('Insert posts in db end')

    def get_images(self, number_images):
        images = [self.faker.unique.image_url() for _ in range(number_images)]
        for index, url in enumerate(images):
            with open(f'../src/images_for_data_migration/{index}.jpg', 'wb') as file:
                resource = requests.get(url)
                file.write(resource.content)

        return images

    def generate_companies(self, number_companies):
        print('Start generating companies')
        companies = []

        for i in range(1, number_companies+1):
            company = {
                'id': i,
                'name': self.faker.unique.company(),
                'url': self.faker.unique.url(),
                'address': self.faker.unique.address(),
                'date_created': self.faker.date(),
            }
            companies.append(company)
        print('Generating companies ends')
        return companies

    def generate_users(self, number_users):
        print('Start generating users')
        users = []
        for i in range(2, number_users+2):
            user = {
                'id': i,
                'email': self.faker.unique.ascii_email(),
                'password': self.faker.bban(),
                'first_name': self.faker.first_name(),
                'last_name': self.faker.last_name(),
                'user_type': 'client',
                'telephone_number': self.faker.msisdn(),
            }
            users.append(user)
        print('Generating users ends')
        return users

    def generate_posts(self, number_posts):
        print('Start generating posts')
        topics = ['test', 'new', 'hot', 'news', 'people', 'dev', 'music', 'games']
        posts = []
        i = 0
        for user in self.users:
            for _ in range(number_posts):
                post = {
                    'id': i,
                    'title': f'{self.faker.word()}_{i}',
                    'user_id': user['id'],
                    'text': self.faker.text(max_nb_chars=50),
                    'topic': topics[random.randint(0, len(topics) - 1)]
                }
                i += 1
                posts.append(post)
        print('Generating posts ends')
        return posts


data = DataMigration(10, 200, 30)
data.run()
print('DATABASE SUCCESSFULLY FILLED')
