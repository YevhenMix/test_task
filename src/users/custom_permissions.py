import logging

from rest_framework.permissions import BasePermission
from posts.models import Post


class IsAdminOrSuperAdmin(BasePermission):
    """
    Allows access only to admin or super admin users.
    """

    def has_permission(self, request, view):
        try:
            user_type = request.user.user_type
        except AttributeError:
            user_type = 'anonymous'
        return bool(request.user.email and (user_type == 'super_admin' or user_type == 'admin'))


class IsOwnerOrAccessDenied(BasePermission):

    def has_permission(self, request, view):
        if request.user.user_type == 'super_admin' or request.user.user_type == 'admin':
            return True

        post_id = request.path.split('/')[-1]
        try:
            post = Post.objects.get(id=int(post_id))
        except Post.DoesNotExist:
            return True
        return bool(request.user.email and post.user_id == request.user)


class IsOwnerAllPostsOrAccessDenied(BasePermission):

    def has_permission(self, request, view):
        if request.user.user_type == 'super_admin' or request.user.user_type == 'admin':
            return True

        posts = request.data.get('posts_to_update')
        logging.getLogger()
        print(posts)
        print(type(posts))
        for post in posts:
            print(post)
            post_id = post.get('id')
            try:
                post_id = int(post_id)
            except Exception as e:
                return True
            try:
                real_post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return True
            if real_post.user_id.id != request.user.id:
                return False
        return True


class IsEmployeeOrAccessDenied(BasePermission):

    def has_object_permission(self, request, view, obj):

        return bool(request.user.email and obj.id == request.user.company_id)
