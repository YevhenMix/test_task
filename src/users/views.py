import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, CreateUserSerializer, UserUpdateSerializer, UserListSerializers
from .custom_permissions import IsAdminOrSuperAdmin, IsOwnerOrAccessDenied

SOFT_DELETE_PARAM = openapi.Parameter('soft_delete', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN)


class UsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='List of all users',
        operation_description='Return list of all users with base information about there company',
        operation_id='All Users',
        responses={
            200: UserListSerializers(many=True)
        }
    )
    def get(self, request):
        users = User.objects.select_related('company_id').all()

        response = UserListSerializers.get_response_with_company_info(users)

        return Response(response, status=status.HTTP_200_OK)


class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='Get info about one user',
        operation_description='Return info about one user',
        operation_id='One User',
        responses={
            200: UserSerializer(many=True),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "User with id=50 does not exist",
                }
            })
        }
    )
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response = {'error': f'User with id={user_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Update info about one user',
        operation_description='Update info about one user',
        operation_id='Update User',
        request_body=UserUpdateSerializer(),
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully update user with id=1",
                }
            }),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "User with id=50 does not exist",
                }
            }),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "detail": "Email field is invalid",
                }
            }),
        }
    )
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response = {'error': f'User with id={user_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = UserUpdateSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Successfully update user with id={user_id}'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Delete one user',
        operation_description='Delete one user permanent if query param soft_delete = false or not transferred else'
                              'mark user as deleted_user',
        operation_id='Delete User',
        manual_parameters=[SOFT_DELETE_PARAM, ],
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully delete user with id=1",
                }
            }),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "User with id=50 does not exist",
                }
            }),
        }
    )
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response = {'error': f'User with id={user_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        soft_delete = request.GET.get('soft_delete', 'false')

        if soft_delete and soft_delete == 'true':
            user.is_active = False
            user.is_deleted = True
            user.save()
        else:
            user.delete()

        return Response({'message': f'Successfully delete user with id={user_id}'}, status.HTTP_200_OK)


class UserCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='Create one user',
        operation_description='Create one user',
        operation_id='Create User',
        request_body=CreateUserSerializer(),
        responses={
            200: UserSerializer(),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "detail": "Email field is invalid",
                    "message": "You are can't create user with user_type=super_admin"
                }
            }),
        }
    )
    def post(self, request):
        request_user = request.user.user_type

        data = request.data
        user_type = data.get('user_type', 'client')
        if request_user == 'super_admin':
            serializer = CreateUserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request_user == 'admin' and user_type == 'client':
            serializer = CreateUserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': f"You are can't create user with user_type={user_type}"},
                            status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrAccessDenied]

    @swagger_auto_schema(
        operation_summary='Info about you account',
        operation_description='Return info about your account',
        operation_id='Your Account',
        responses={
            200: UserSerializer()
        }
    )
    def get(self, request):
        user_id = request.user.id

        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Update info about your account',
        operation_description='Update info about your account',
        operation_id='Update Your Account',
        request_body=UserUpdateSerializer(),
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully update user with id=1",
                }
            }),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "detail": "Email field is invalid",
                }
            }),
        }
    )
    def patch(self, request):
        user_id = request.user.id

        user = User.objects.get(id=user_id)
        data = request.data
        serializer = UserUpdateSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Successfully update user with id={user_id}'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
