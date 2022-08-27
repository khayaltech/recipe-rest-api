"""
URLs for recipe APIs
"""
from django.urls import path, include
from .views import IngredientViewset, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
app_name = 'recipe'
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewset)

urlpatterns = [
    path('', include(router.urls))
]
