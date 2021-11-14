import logging

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer
from posts.models import Post
from posts.serializers import PostSerializer
from .models import Company


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

    @staticmethod
    def generate_full_result(companies):
        result = []
        for company in companies:
            company_data = {}
            company_data.update(company)

            company_id = company.get('id')
            users = User.objects.select_related('company_id').filter(company_id=company_id)
            user_serializer = UserSerializer(users, many=True)

            for user in user_serializer.data:
                user_id = user.get('id')
                posts = Post.objects.select_related('user_id').filter(user_id=user_id)
                post_serializer = PostSerializer(posts, many=True)
                user['posts'] = post_serializer.data

            company_data['employees'] = user_serializer.data

            result.append(company_data)
        return result


class CompanyUpdateSerializer(ModelSerializer):
    name = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    address = serializers.CharField(required=False)
    date_created = serializers.DateField(required=False)
    logo = serializers.FileField(required=False)

    class Meta:
        model = Company
        fields = ('name', 'url', 'address', 'date_created', 'logo')

