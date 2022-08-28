"""
Views for recipe APIs
"""
from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (IngredientSerializer,
                                RecipeDetailSerializer,
                                RecipeSerializer,
                                TagSerializer,
                                RecipeImageSerializer)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import (mixins,
                            viewsets,
                            status)
from rest_framework.decorators import action
from rest_framework.response import Response


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage User API"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return Recipe.objects.filter(user=self.request.user.id).order_by('id')

    def get_serializer_class(self):
        """Changing the default behaviour of serializer class"""
        if (self.action == 'list'):
            return RecipeSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        else:
            return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseAttrRecipeViewset(mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Base viewset for recipe attributes"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
