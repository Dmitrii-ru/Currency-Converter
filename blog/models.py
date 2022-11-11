from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Profile

class News(models.Model):
    title = models.CharField('Название статьи', max_length=1000,blank=True)
    text = models.TextField('Основной текст статьи',blank=True)
    date = models.DateTimeField('Дата', default=timezone.now)
    avtor = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE,blank=False,null=True)
    views = models.IntegerField('Просмотры', default=0,blank=False)
    link = models.CharField('Ссылка на источник', max_length=100, blank=False)

    def get_absolute_url(self):
        return reverse ('news_detail',kwargs={'pk':self.pk})

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Comment(models.Model):
    post = models.ForeignKey(News, related_name='comments',on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.comment, self.post)