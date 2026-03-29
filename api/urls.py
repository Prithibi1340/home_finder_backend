from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, LoginView, CreatePostView, AddCommentView, VideoStreamView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('posts/', CreatePostView.as_view(), name='all_posts'),
    path('posts/create/', CreatePostView.as_view(), name='create_post'),
    path('videos/<int:video_id>/stream/', VideoStreamView.as_view(), name='video_stream'),
    path('comments/add/', AddCommentView.as_view(), name='add_comment'),
]
