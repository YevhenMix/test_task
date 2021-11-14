from django.db import models


class Post(models.Model):
    title = models.CharField('Title Post', max_length=40, unique=True, null=False, blank=False)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    text = models.TextField('Text for Post')
    topic = models.CharField('Topic Post', max_length=20, null=False, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
