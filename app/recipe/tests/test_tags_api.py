from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


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
