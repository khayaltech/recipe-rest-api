"""
Views for recipe APIs
"""
from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (IngredientSerializer,
                                RecipeDetailSerializer,
                                RecipeSerializer,
                                TagSerializer)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage User API"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return Recipe.objects.filter(user=self.request.user.id).order_by('id')

    def get_serializer_class(self):
        """Changing the default behaviour of serializer class"""
        if (self.action == 'list'):
            return RecipeSerializer
        else:
            print(self.action)
            return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BaseAttrRecipeViewset(mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Base viewset for recipe attributes"""

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtering queryset to authenticted user"""
        return self.queryset.filter(user=self.request.user.id).order_by('-name')


class TagViewSet(BaseAttrRecipeViewset):
    "Manage tags in the database"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewset(BaseAttrRecipeViewset):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
