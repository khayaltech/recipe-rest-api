"""
Views for recipe APIs
"""
from core.models import Recipe, Tag
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer, TagSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets


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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    "Manage tags in the database"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtering queryset to authenticted user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
