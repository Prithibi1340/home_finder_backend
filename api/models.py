from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)   
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=255,null=True,)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    house_number = models.CharField(max_length=50)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    description = models.TextField(blank=True)
    geo_location = models.CharField(max_length=255)
    images = models.ManyToManyField('Image', related_name='posts', blank=True)
    videos = models.ManyToManyField('Video', related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_rented = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)
    
    def __str__(self):
        return f"Post by {self.user.email} - {self.house_number}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.post.house_number}"

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images')
    image = models.ImageField(upload_to='post_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Post ID {self.post.id}"

class Video(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_videos')
    video = models.FileField(upload_to='post_videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for Post ID {self.post.id}"