from django import forms
from django.contrib.auth.models import User
from .models import News ,Comment
from django.forms import ModelForm


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'text', 'link']


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']


