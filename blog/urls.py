from django.urls import path
from . import views

urlpatterns = [
    path('', views.ShowAllBlogView.as_view(), name='blog'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('<int:pk>/update/', views.UpdatePostView.as_view(), name='news_update'),
    path('<int:pk>/delete/', views.DeletePostView.as_view(), name='news_delete'),
    path('user/<str:username>/', views.ShowAllAvtorBlogView.as_view(), name='news_avtor'),
    path('update_news', views.news_parser, name='update_news')
]
