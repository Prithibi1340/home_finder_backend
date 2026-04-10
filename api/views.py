import mimetypes
import os
import re
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Post, Comment, Video
from .serializers import UserSerializer, PostSerializer, CommentSerializer


def iter_file_range(file_path, start, end, chunk_size=8192):
    with open(file_path, 'rb') as stream:
        stream.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk = stream.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk

class RegisterView(APIView):
    def post(self, request):
        data = request.data.copy()
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()  # Save and get the user instance
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data['email'])
            if check_password(data['password'], user.password):
                user_data = UserSerializer(user).data  # Serialize user details
                return Response({"message": "Login successful", "user": user_data}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        return self._update_user(request, user_id, partial=False)

    def patch(self, request, user_id):
        return self._update_user(request, user_id, partial=True)

    def _update_user(self, request, user_id, partial):
        user = get_object_or_404(User, user_id=user_id)
        data = {}
        if hasattr(request.data, 'lists'):
            for key, values in request.data.lists():
                data[key] = values if len(values) > 1 else values[0]
        else:
            data = dict(request.data)

        if 'profile_picture' in request.FILES:
            data['profile_picture'] = request.FILES['profile_picture']

        serializer = UserSerializer(user, data=data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    

class CreatePostView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    
    
    def post(self, request):
        data = {}
        if hasattr(request.data, 'lists'):
            for key, values in request.data.lists():
                data[key] = values if len(values) > 1 else values[0]
        else:
            data = dict(request.data)
        uploaded_images = request.FILES.getlist('uploaded_images')
        uploaded_videos = request.FILES.getlist('uploaded_videos')
        if uploaded_images:
            data['uploaded_images'] = uploaded_images
        if uploaded_videos:
            data['uploaded_videos'] = uploaded_videos
        if getattr(request.user, 'is_authenticated', False):
            data['user'] = request.user.id
        serializer = PostSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        posts = Post.objects.all()

        visibility = request.query_params.get('visibility', 'all').lower()
        address = request.query_params.get('address', '').strip()

        if visibility == 'male':
            posts = posts.filter(onlyfor_male=True)
        elif visibility == 'female':
            posts = posts.filter(onlyfor_female=True)
        elif visibility not in ('all', ''):
            return Response(
                {'error': "Invalid visibility. Use 'male', 'female', or 'all'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if address:
            posts = posts.filter(address__icontains=address)

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDeleteView(APIView):
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoStreamView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)

        if not video.video:
            return Response({'error': 'Video file not found'}, status=status.HTTP_404_NOT_FOUND)

        file_path = video.video.path
        if not os.path.exists(file_path):
            return Response({'error': 'Video file not found'}, status=status.HTTP_404_NOT_FOUND)

        file_size = os.path.getsize(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        range_header = request.headers.get('Range')
        if not range_header:
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(file_size)
            return response

        range_match = re.match(r'bytes=(\d*)-(\d*)', range_header)
        if not range_match:
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{file_size}'
            return response

        start_str, end_str = range_match.groups()
        if start_str == '' and end_str == '':
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{file_size}'
            return response

        if start_str == '':
            suffix_length = int(end_str)
            start = max(file_size - suffix_length, 0)
            end = file_size - 1
        else:
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1

        if start >= file_size or start > end:
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{file_size}'
            return response

        end = min(end, file_size - 1)
        content_length = end - start + 1

        response = StreamingHttpResponse(
            iter_file_range(file_path, start, end),
            status=206,
            content_type=content_type,
        )
        response['Accept-Ranges'] = 'bytes'
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Content-Length'] = str(content_length)
        return response

class CommentListView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddCommentView(APIView):
    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

