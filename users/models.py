from django.contrib.auth.models import User
from django.db import models
from PIL import Image
CHOICES = (('b', "+18"), ('s', '-18'))

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    img = models.ImageField('Фото пользователя', default='default.png', upload_to='user_images')
    adult = models.CharField('Пол пользователя ',choices=CHOICES, max_length=15, default='m' )
    subscription = models.BooleanField(verbose_name='Подписка', default=True, blank=False)

    def __str__(self):
        return f" {self.user.username}"


    def save(self, *args, **kwargs):
        super().save()
        image = Image.open(self.img.path)
        if image.height > 100 or image.width > 100:
            resize = (100, 100)
            image.thumbnail(resize)
            image.save(self.img.path)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'