import logging

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import User
from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'user_type', 'company_id', 'avatar', 'telephone_number')


class UserListSerializers(ModelSerializer):
    company = serializers.JSONField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'user_type', 'telephone_number', 'avatar', 'company')

    @staticmethod
    def get_response_with_company_info(users):
        logging.getLogger()
        for user in users:
            user.company = dict()
            user.company['name'] = user.company_id.name
            user.company['url'] = user.company_id.url
            user.company['address'] = user.company_id.address
            user.company['date Created'] = user.company_id.date_created
        serializer = UserListSerializers(users, many=True)
        return serializer.data


class CreateUserSerializer(ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=128, min_length=8)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    user_type = serializers.ChoiceField(['client', 'admin', 'super_admin'])
    avatar = serializers.FileField(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'user_type', 'company_id', 'avatar', 'telephone_number', 'password')

    def create(self, validated_data):
        user = super(CreateUserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(ModelSerializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    avatar = serializers.FileField(required=False)
    telephone_number = PhoneNumberField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'telephone_number')

