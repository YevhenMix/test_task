import logging

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.custom_permissions import IsAdminOrSuperAdmin, IsOwnerOrAccessDenied, IsOwnerAllPostsOrAccessDenied
from .models import Post
from .serializers import PostSerializer, PostsSerializer, PostUpdateSerializer, PostBulkUpdateSerializer


TITLE_PARAM = openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING)
TEXT_PARAM = openapi.Parameter('text', openapi.IN_QUERY, type=openapi.TYPE_STRING)
TOPIC_PARAM = openapi.Parameter('topic', openapi.IN_QUERY, type=openapi.TYPE_STRING)
COMPANY_PARAM = openapi.Parameter('company', openapi.IN_QUERY, type=openapi.TYPE_STRING)


class PostsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='List of all posts',
        operation_description='Return list of all posts, or can filter result by some query param',
        operation_id='All Posts',
        manual_parameters=[TITLE_PARAM, TEXT_PARAM, TOPIC_PARAM, COMPANY_PARAM],
        responses={
            200: PostsSerializer(many=True)
        }
    )
    def get(self, request):
        title = request.GET.get('title', '')
        text = request.GET.get('text', '')
        topic = request.GET.get('topic', '')
        company = request.GET.get('company', '')

        if title or text or topic or company:
            posts = Post.objects.select_related('user_id').filter(
                Q(title__icontains=title) &
                Q(text__icontains=text) &
                Q(user_id__company_id__name__icontains=company) &
                Q(topic__icontains=topic)
            )
        else:
            posts = Post.objects.select_related('user_id').all()

        response = PostsSerializer(posts, many=True)

        return Response(response.data, status=status.HTTP_200_OK)


class PostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrAccessDenied]

    @swagger_auto_schema(
        operation_summary='One Post',
        operation_description='Return one post',
        operation_id='One Post',
        responses={
            200: PostSerializer(),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "Post with id=50 does not exist",
                }
            })
        }
    )
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            response = {'error': f'Post with id={post_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Update post data',
        operation_description='Update post data',
        operation_id='Update Post',
        request_body=PostUpdateSerializer(),
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully update post with id=1",
                }
            }),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "Post with id=50 does not exist",
                }
            }),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "detail": "Title field is invalid",
                }
            }),
        }
    )
    def patch(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            response = {'error': f'Post with id={post_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = PostUpdateSerializer(post, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Successfully update post with id={post_id}'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Delete one post',
        operation_description='Delete one post',
        operation_id='Delete Post',
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully delete post with id=1",
                }
            }),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "Post with id=50 does not exist",
                }
            }),
        }
    )
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            response = {'error': f'Post with id={post_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        post.delete()

        return Response({'message': f'Successfully delete post with id={post_id}'}, status.HTTP_200_OK)


class PostCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Create post',
        operation_description='Create Post',
        operation_id='Create Post',
        request_body=PostSerializer(),
        responses={
            200: PostSerializer(),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "message": "You're can't create post for another user",
                    "detail": "Field title is invalid"
                }
            }),
        }
    )
    def post(self, request):
        data = request.data
        if request.user.user_type == 'client' and int(data['user_id']) != int(request.user.id):
            return Response({'message': "You're can't create post for another user"}, status=status.HTTP_400_BAD_REQUEST)

        if not data.get('user_id'):
            data['user_id'] = request.user.id
        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostBulkUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerAllPostsOrAccessDenied]

    @swagger_auto_schema(
        operation_summary='Update few posts at once',
        operation_description='Update few posts at one request',
        operation_id='Bulk Update Post',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'posts_to_update': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                    'text': openapi.Schema(type=openapi.TYPE_STRING),
                    'topic': openapi.Schema(type=openapi.TYPE_STRING),
                }),
            ),
        }),
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully update posts"
                }
            }),
        }
    )
    def patch(self, request):
        posts = request.data.get('posts_to_update')

        post_to_update = []
        for post in posts:
            post_id = post.get('id', None)
            try:
                post_id = int(post_id)
            except Exception as e:
                return Response({'error': 'Field id must be integer'}, status=status.HTTP_400_BAD_REQUEST)
            title = post.get('title', '')
            text = post.get('text', '')
            topic = post.get('topic', '')
            try:
                real_post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return Response({'error': f'Post with id={post_id} does not exist'}, status.HTTP_404_NOT_FOUND)

            exited_title = Post.objects.filter(title=title)
            if exited_title:
                return Response({'error': f'Post with title={title} already exist'}, status=status.HTTP_400_BAD_REQUEST)

            real_post.title = title or real_post.title
            real_post.text = text or real_post.text
            real_post.topic = topic or real_post.topic

            post_to_update.append(real_post)

        Post.objects.bulk_update(post_to_update, ['title', 'text', 'topic'])

        return Response({'message': 'Successfully update posts'}, status=status.HTTP_200_OK)


class CompanyPostsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_summary='List of all posts in one company',
        operation_description='Return list of all posts in your company',
        operation_id='Your Company Posts',
        responses={
            200: PostSerializer(many=True)
        }
    )
    def get(self, request):
        posts = Post.objects.select_related('user_id__company_id').filter(user_id__company_id_id=request.user.company_id.id)
        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
