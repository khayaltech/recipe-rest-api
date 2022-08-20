"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Check that user created through email succesfully"""
        email = 'test@example.com'
        password = '1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Check that email which is used to register is normalized."""
        sample_emails = [
            ['test@EXAMPLE.com', 'test@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, password='1234')
            self.assertEqual(user.email, expected)

    def test_new_user_raise_error_without_email(self):
        """Test that creating a user withot email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "1234")

    def test_create_superuser(self):
        """Test for creating superuser"""
        user = get_user_model().objects.create_superuser(
            "testuser@example.com",
            '1234')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_model(self):
        """Test for creating Recipe model"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testing321")
        res = models.Recipe.objects.create(
            user=user,
            title='My launch name',
            time_in_minutes=5,
            price=Decimal("5.55"),
            description='Sample recipe description'
        )
        self.assertEqual(str(res), res.title)
