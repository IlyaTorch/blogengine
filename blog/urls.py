from django.urls import path
from . import views

urlpatterns = [
    path('', views.posts_list, name='posts_list_url'),
    path('posts/<str:slug>/', views.PostDetail.as_view(), name='post_detail_url'),
    path('tags/', views.tags_list, name='tags_list_url'),
    path('tags/create', views.TagCreate.as_view(), name='tag_create_url'),
    path('tags/<str:slug>', views.TagDetail.as_view(), name='tag_detail_url'),
]
