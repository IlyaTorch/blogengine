from django.urls import path
from . import views

urlpatterns = [
    path('', views.posts_list, name='posts_list_url'),
    path('posts/<str:slug>/', views.post_detail, name='post_detail_url'),
]
