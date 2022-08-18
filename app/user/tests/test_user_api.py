"""Tests for user API"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of user API"""
    def setUp(self):
        self.client = APIClient()

    def test_user_created_succesfully(self):
        """Test creating a user is a succesful"""
        payload = {
            "email": "khayal@example.com",
            "name": "khayalfarajov",
            "password": "testing321"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn(payload['password'], res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned when user exist with email"""
        payload = {
            "email": "khayal@example.com",
            "name": "khayalfarajov",
            "password": "testing321"
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error when length of password is less than 5"""
        payload = {
            "email": "khayalfarajov@gmail.com",
            "name": "khayalfarajov",
            "password": "test"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""

        user_detail = {
            "email": "khayalfarajov@gmail.com",
            "name": "khayalfarajov",
            "password": "mypassword"
        }

        create_user(**user_detail)

        payload = {
            'email': user_detail['email'],
            "password": user_detail['password']
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_bad_credentials(self):
        """Test returns error if credentials invalid."""

        user_detail = {
            "email": "khayalfarajov@gmail.com",
            "name": "khayalfarajov",
            "password": "goodpass"
        }
        create_user(**user_detail)
        payload = {
            'email': user_detail['email'],
            "password": "badpass"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""

        payload = {
            'email': "khayalfarajov@gmail.com",
            "password": ""
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
