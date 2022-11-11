from django.urls import path

from . import views

urlpatterns = [
    path('', views.exchenge, name='index'),
    path('upcurr100/',views.fill_up_a_purse, name='fill_up_a_purse'),
    path('loadcurr/',views.upcurrdefauto, name='loadcurr'),
    # path('exchenge', views.exchenge, name='exchenge')
]
