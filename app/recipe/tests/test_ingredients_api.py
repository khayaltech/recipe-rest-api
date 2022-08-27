from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTestAPI(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestAPI(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='khayalfarajov@gmail.com', password='testing321')

        self.client.force_authenticate(self.user)

    def test_retrieving_ingredients(self):
        """Test retrieving list of tags"""
        Ingredient.objects.create(user=self.user, name="ingredient1")
        Ingredient.objects.create(user=self.user, name="ingredient2")

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test retrieving list of tags for authenticated user"""
        user2 = create_user(email='reandom@gmail.com', password='testing321')
        Ingredient.objects.create(user=user2, name="ingredient1")
        Ingredient.objects.create(user=self.user, name="ingredient2")

        ingredient = Ingredient.objects.get(user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)
