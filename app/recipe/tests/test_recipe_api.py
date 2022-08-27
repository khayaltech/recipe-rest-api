from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from core.models import Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


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
        self.user = create_user(email='khayalfarajov@gmail.com', password='testing321')
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

    def test_get_recipe_detail(self):
        """Test for  getting the recipe detail"""
        recipe = create_recipe(user=self.user)
        serializer = RecipeDetailSerializer(recipe)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""

        payload = {
            "title": "Sample recipe title",
            "time_in_minutes": 30,
            "price": Decimal("5.30")
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of recipe"""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe tittle",
            link=original_link
        )
        payload = {"title": "New Recipe Title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update"""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe tittle",
            link=original_link,
            description='Sample recipe description'
        )
        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_in_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        print(recipe)
        for k, v in payload.items():
            self.assertEquals(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test for deleting recipe"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test for checking error when one user tried to another's recipe"""
        new_user = create_user(email='oruj@mail.com', password='testing321')
        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_creating_recipe_with_new_tags(self):
        """Test for creating tags"""
        payload = {
            'title': 'Azerbaiajani kabab',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'Kabab description',
            'time_in_minutes': 10,
            'price': Decimal('5.50'),
            'tags': [{'name': 'Azeri'}, {'name': 'Delicious'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test is intended for checking recipe is created with tags which already exists"""
        tag_azerbaijani = Tag.objects.create(user=self.user, name='Azerbaijani')
        payload = {
            'title': 'Azerbaiajani kabab',
            'link': 'https://example.com/new-recipe.pdf',
            'time_in_minutes': 10,
            'price': Decimal('5.50'),
            'tags': [{'name': 'Azerbaijani'}, {'name': 'Delicious'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = recipes[0]
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(tag_azerbaijani, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test create tag when updating a recipe."""
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'dinner'}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        new = Tag.objects.get(name='dinner')
        self.assertIn(new, recipe.tags.all())

    def test_assign_tag_on_update(self):
        """Test assign existing tag to recipe when updating recipe"""
        recipe = create_recipe(user=self.user)
        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        recipe.tags.add(tag_lunch)

        tag_dinner = Tag.objects.create(user=self.user, name="Dinner")
        payload = {'tags': [{'name': 'Dinner'}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format='json')
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag_lunch, recipe.tags.all())
        self.assertIn(tag_dinner, recipe.tags.all())

    def test_clear_tags_on_update(self):
        """Test clearing a recipes tags."""

        recipe = create_recipe(user=self.user)
        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        recipe.tags.add(tag_lunch)
        payload = {"tags": []}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_creating_recipe_with_new_ingredients(self):
        """Test for creating ingredients"""
        payload = {
            'title': 'Azerbaiajani kabab',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'Kabab description',
            'time_in_minutes': 10,
            'price': Decimal('5.50'),
            'ingredients': [{'name': 'pepper'}, {'name': 'salt'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        print(recipe.ingredients.count())

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=ingredient['name']
            )
            self.assertTrue(exists)

    def test_creating_recipe_with_existing_ingredients(self):
        """Test is intended for checking recipe is created with ingredients which already exists"""

        ingreident_pepper = Ingredient.objects.create(user=self.user, name="pepper")
        payload = {
            'title': 'Azerbaiajani kabab',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'Kabab description',
            'time_in_minutes': 10,
            'price': Decimal('5.50'),
            'ingredients': [{'name': 'pepper'}, {'name': 'salt'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingreident_pepper, recipe.ingredients.all())

    def test_create_ingredients_on_update(self):
        """Test create ingredients when updating recipe"""

        recipe = create_recipe(user=self.user)
        payload = {
            'ingredients': [{'name': 'pepper'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        ingredient = Ingredient.objects.get(name='pepper')
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_assing_ingredients_on_update(self):
        """Test assign ingredients when updating recipe"""
        ingredient = Ingredient.objects.create(user=self.user, name='pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {
            'ingredients': [{'name': 'pepper'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        ingredient = Ingredient.objects.get(name='pepper')
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_clear_ingredients_on_update(self):
        """Test clearing a recipes ingredients."""

        recipe = create_recipe(user=self.user)
        ingredient_pepper = Ingredient.objects.create(user=self.user, name="pepper")
        recipe.ingredients.add(ingredient_pepper)
        payload = {"ingredients": []}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
