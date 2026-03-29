from rest_framework import serializers
from .models import User, Post, Comment, Image, Video

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'profile_picture', 'email', 'name', 'password', 'phone_number', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'post', 'image', 'uploaded_at']

class VideoSerializer(serializers.ModelSerializer):
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'post', 'video', 'stream_url', 'uploaded_at']

    def get_stream_url(self, obj):
        request = self.context.get('request')
        relative_url = f'/videos/{obj.id}/stream/'
        if request is not None:
            return request.build_absolute_uri(relative_url)
        return relative_url

class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    uploaded_videos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['id', 'description', 'rent_price', 'user', 'house_number', 'geo_location', 'images', 'videos', 'uploaded_images', 'uploaded_videos', 'created_at', 'updated_at', 'is_rented', 'likes', 'dislikes']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        uploaded_videos = validated_data.pop('uploaded_videos', [])
        likes = validated_data.pop('likes', [])
        dislikes = validated_data.pop('dislikes', [])
        post = Post.objects.create(**validated_data)

        if likes:
            post.likes.set(likes)

        if dislikes:
            post.dislikes.set(dislikes)

        for image_file in uploaded_images:
            image_instance = Image.objects.create(post=post, image=image_file)
            post.images.add(image_instance)

        for video_file in uploaded_videos:
            video_instance = Video.objects.create(post=post, video=video_file)
            post.videos.add(video_instance)

        return post

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'updated_at']