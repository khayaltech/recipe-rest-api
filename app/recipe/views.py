"""
Views for recipe APIs
"""
from rest_framework import viewsets
from core.models import Recipe
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage User API"""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return Recipe.objects.filter(user=self.request.user).order_by('id')

    def get_serializer_class(self):
        """Changing the default behaviour of serializer class"""
        if (self.action == 'list'):
            return RecipeSerializer
        else:
            return self.serializer_class
