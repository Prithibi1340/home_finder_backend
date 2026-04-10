from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, LoginView, UserDetailView, CreatePostView, PostDeleteView, CommentListView, AddCommentView, VideoStreamView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('posts/', CreatePostView.as_view(), name='all_posts'),
    path('posts/create/', CreatePostView.as_view(), name='create_post'),
    path('posts/delete/<int:post_id>/', PostDeleteView.as_view(), name='post_detail'),
    path('videos/<int:video_id>/stream/', VideoStreamView.as_view(), name='video_stream'),
    path('comments/<int:post_id>/', CommentListView.as_view(), name='get_comments'),
    path('comments/add/', AddCommentView.as_view(), name='add_comment'),
]
