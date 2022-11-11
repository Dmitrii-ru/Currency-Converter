from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.edit import FormMixin

from .forms import CreateCommentForm
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup as bs4


# Показываем все новости
class ShowAllBlogView(ListView):
    model = News
    context_object_name = 'news'
    paginate_by = 10
    ordering = ['-date']


# Показываем все новости автора
class ShowAllAvtorBlogView(ListView):
    model = News
    context_object_name = 'news'
    paginate_by = 10
    ordering = ['-views']

    template_name = 'blog/news_avtor.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return News.objects.filter(avtor=user).order_by('-date')

    def get_context_data(self, **kwards):
        context = super(ShowAllAvtorBlogView, self).get_context_data(**kwards)
        context['title'] = f"Станица {self.kwargs.get('username')}"
        return context


# Показываем выбранную новость
class NewsDetailView(DetailView, FormMixin):
    model = News
    form_class = CreateCommentForm
    success_url = reverse_lazy('blog')

    # контекст и +1 просмотр
    def get_context_data(self, **kwargs):
        print('context')
        context = super(NewsDetailView, self).get_context_data()
        object = super(NewsDetailView, self).get_object()
        object.views += 1
        object.save()
        context['form'] = self.form_class
        context['comment'] = Comment.objects.filter(post=self.get_object()).only('user', 'comment', 'created').order_by(
            '-created')
        return context
     # Добавляем новость
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if request.user.is_authenticated:
            if form.is_valid() and request.user.is_authenticated:
                Comment(comment=form.cleaned_data['comment'], user=request.user, post=self.get_object()).save()
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect('user')


class CreatePostView(LoginRequiredMixin, CreateView):
    model = News
    template_name = 'blog/create_post.html'

    fields = ['title', 'text']

    def form_valid(self, form):
        form.instance.avtor = self.request.user

        return super().form_valid(form)

    def get_context_data(self, **kwards):
        context = super(CreatePostView, self).get_context_data(**kwards)
        context['title'] = 'Добавить статью'
        context['btn'] = 'Добавить'
        return context


class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = News
    template_name = 'blog/create_post.html'
    fields = ['title', 'text']

    def get_context_data(self, **kwards):
        context = super(UpdatePostView, self).get_context_data(**kwards)
        context['title'] = 'Обновление статьи'
        context['btn'] = 'Обновить'
        return context

    def form_valid(self, form):
        form.instance.avtor = self.request.user
        return super().form_valid(form)

    def test_func(self):
        news = self.get_object()
        if self.request.user == news.avtor:
            return True
        return False


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = News
    success_url = reverse_lazy('blog')
    template_name = 'blog/news_delete.html'

    def post(self, request, *args, **kwargs):
        news = get_object_or_404(News, pk=self.kwargs.get('pk'))
        if request.user == news.avtor:
            news.delete()
            return redirect('blog')
        else:
            return redirect('user')

    def test_func(self):

        news = self.get_object()
        if self.request.user == news.avtor:
            return True
        return False

# Парсим новости
def parser_page(page):
    news_old_list = News.objects.all()
    print(news_old_list)
    headers = {
        'accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    url = f'http://www.finmarket.ru{page}'
    session = requests.Session()
    req = session.get(url, headers=headers)
    try:
        if req.status_code == 200:
            soup = bs4(req.content, 'html.parser')
            divs = soup.find('div', class_='news_content')
            title = divs.find('h1', class_='title').text
            href = url
            text = divs.find('div', class_='body').text
            if str(href) not in news_old_list:
                News(title=title, text=text, link=href).save()
            redirect('blog')
    except Exception:
        print('Ошибка URL parser_page')

# Собираем ссылки на новости убираем дубли ссылок поправляем в parser_page
def news_parser(request):
    headers = {
        'accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    url = 'http://www.finmarket.ru/news/?nt=1&pg=1'
    session = requests.Session()
    req = session.get(url, headers=headers)
    news_list = set()
    try:
        if req.status_code == 200:
            soup = bs4(req.content, 'html.parser')
            print('200', 'news_parser')
            div_page = soup.find('div', class_='ind_article').find_all('a')
            for h in div_page:
                if h.get('href') is not None and 'pg' not in h.get('href'):
                    news_list.add(h.get('href'))
            for page in news_list:
                parser_page(page)
            return redirect('blog')
        else:
            print('Ошибка')
    except Exception:
        print('Ошибка URL news_parser')
