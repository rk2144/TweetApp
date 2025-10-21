from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('tweets/', views.tweet_list, name='tweet_list'),
    path('tweet/', views.tweet_list),
    path('<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('<int:tweet_id>/edit/', views.tweet_edit, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('register/', views.register, name='register'),
    path('<int:tweet_id>/like_ajax/', views.like_tweet_ajax, name='like_tweet_ajax'),

    # ✅ New login URL
    path('login/', CustomLoginView.as_view(), name='login'),
]
