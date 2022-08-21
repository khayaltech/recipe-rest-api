from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from core.models import Recipe
from django.contrib.auth import get_user_model
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    defaults = {
        "title": "Sample recipe title",
        "time_in_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample Description",
        "link": "http://example.com/recipe.pdf/"
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **params)
    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicTestAPI(TestCase):
    """Tests which don't require authentication"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestAPI(TestCase):
    """Tests which  require authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="khayalfarajov@gmail.com",
            password="testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving the list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_limited_to_user(self):
        """Test retrieving the list of recipes is limited to authentcated users"""
        other_user = create_user(email='other@example.com', password='test123')

        create_recipe(user=self.user)
        create_recipe(user=other_user)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
