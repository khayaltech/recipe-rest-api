"""
URLs for recipe APIs
"""
from django.urls import path, include
from .views import RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
app_name = 'recipe'
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls))
]
