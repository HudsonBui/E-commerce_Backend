"""
Tests for user API endpoints.
"""
import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from user.serializers import UserSerializer


CREATE_USER_URL = reverse("user:sign-up")
LOGIN_URL = reverse("user:login")
USER_URL = reverse("user:me")
IMAGE_UPLOAD_URL = reverse("user:upload-image")


# def image_upload_url(user_id):
#     """Create and return an image upload URL."""
#     return reverse("user:upload-image", args=[user_id])


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'user@example.com',
            'password': 'Testpass.12345',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'user@example.com',
            'password': 'Testpass.12345',
            'name': 'Test User'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_wrong_constraints(self):
        """Test an error is returned if password is wrong contraints."""
        payload = {
            'email': 'user@example.com',
            'password': 'pw',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generate token for valid credentials."""
        user_details = {
            'name': 'Test User',
            'email': 'user@example.com',
            'password': 'Testpass.12345',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(LOGIN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(
            email='user@example.com',
            password='Testpass.12345',
        )

        payload = {
            'email': 'user@example.com',
            'password': 'wrong',
        }

        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test returns error if password blank."""
        create_user(
            email='user@example.com',
            password='Testpass.12345',
        )

        payload = {
            'email': 'user@example.com',
            'password': '',
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            name="Test User",
            email="user@example.com",
            password="Testpassword.12345",
            address="123 Test St",
            phone_number="0123456789",
            birthday="1990-01-01",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile successfully."""
        res = self.client.get(USER_URL)
        user = get_user_model().objects.get(id=self.user.id)
        user_serializer = UserSerializer(user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', res.data)
        self.assertEqual(res.data, user_serializer.data)

    def test_post_users_not_allowed(self):
        """Test POST is not allowed for the users endpoint."""
        res = self.client.post(USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test for update user profile."""
        payload = {
            'name': 'Updated Name',
            'password': 'Newpassword.12345',
            'address': '456 Updated St',
            'phone_number': '9876543210',
            'birthday': '1995-01-01',
        }

        res = self.client.patch(USER_URL, payload, format='multipart')

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.address, payload['address'])
        self.assertEqual(self.user.phone_number, payload['phone_number'])
        self.assertEqual(self.user.birthday.isoformat(), payload['birthday'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class ImageUploadTests(TestCase):
    """Test image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            name="Test User",
            email="user@example.com",
            password="Testpassword.12345",
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.user.image.delete()

    def test_upload_image(self):
        """Test uploading an image."""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (100, 100))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.put(IMAGE_UPLOAD_URL, payload, format='multipart')

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.user.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        payload = {'image': 'not_an_image'}
        res = self.client.put(IMAGE_UPLOAD_URL, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
