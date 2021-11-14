import logging

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Post
from users.models import User
from users.serializers import UserSerializer


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostsSerializer(ModelSerializer):
    title = serializers.CharField(required=True)
    user = serializers.SerializerMethodField()
    topic = serializers.CharField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'topic', 'user')

    def get_user(self, obj):
        user = dict()
        user['id'] = obj.user_id.id
        user['First Name'] = obj.user_id.first_name
        user['Last Name'] = obj.user_id.last_name

        return user


class PostUpdateSerializer(ModelSerializer):
    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    topic = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = ('title', 'text', 'topic')


class PostBulkUpdateSerializer(ModelSerializer):
    posts_to_update = serializers.ListField(required=True)

    class Meta:
        model = Post
        fields = ('posts_to_update', )
