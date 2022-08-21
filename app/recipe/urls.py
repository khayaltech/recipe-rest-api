"""
URLs for recipe APIs
"""
from django.urls import path, include
from .views import RecipeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
app_name = 'recipe'
router.register('recipes', RecipeViewSet)
urlpatterns = [
    path('', include(router.urls))
]
