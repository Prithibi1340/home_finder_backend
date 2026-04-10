from django.test import TestCase
from rest_framework.test import APIClient

from .models import Comment, Post, User


class CommentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='owner@example.com',
            password='password123',
            name='Owner',
            phone_number='1234567890',
        )
        self.post = Post.objects.create(
            user=self.user,
            house_number='A-101',
            rent_price=25000,
            description='Sample post',
            geo_location='Kathmandu',
            address='Main Road',
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='First comment',
        )

    def test_get_comments_by_post_id(self):
        response = self.client.get(f'/comments/{self.post.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'First comment')

    def test_add_comment_requires_authentication(self):
        response = self.client.post(
            '/comments/add/',
            {'post': self.post.id, 'content': 'New comment'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_add_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/comments/add/',
            {'post': self.post.id, 'content': 'New comment'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 2)
