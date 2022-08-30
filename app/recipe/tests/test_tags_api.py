from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from decimal import Decimal

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTestAPI(TestCase):
    """Tests which don't require authentication"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestAPI(TestCase):
    """Tests which require authentication"""
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='khayalfarajov@gmail.com', password='testing321')

        self.client.force_authenticate(self.user)

    def test_retrieving_tags(self):
        """Test retrieving the list of tags"""
        Tag.objects.create(user=self.user, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """Test retrieving the list of tags is limited to authentcated users"""
        user2 = create_user(email='orujfarajov@gmail.com', password='testing321')
        Tag.objects.create(user=user2, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")
        tag = Tag.objects.get(user=self.user)

        res = self.client.get(TAGS_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_tag_update(self):
        """Test updating  a tag"""
        tag = Tag.objects.create(user=self.user, name='Dinner')
        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test delete tag"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_tag_other_users_tagerror(self):
        """Test for checking error when one user tried to another's tag"""
        newuser = create_user(email='orujfarajov@gmail.com', password='testing321')
        tag = Tag.objects.create(user=newuser, name='Fastfood')
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_in_minutes=10,
            price=Decimal('2.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_in_minutes=5,
            price=Decimal('5.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_in_minutes=3,
            price=Decimal('2.00'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
