from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet
from users.serializers import FavoritRecipeSerializer

from foodgram.mixins import ListRetriveViewSet
from foodgram.pagination import PageLimitPagination

from .models import Favorites, Ingredient, Recipe, Tag
from .serializers import (GetRecipeSerializer, IngredientSerializer,
                          PostRecipeSerializer, TagSerializer)
from .filters import IngredientSearchFilter, RecipeFilter


class TagViewSet(ListRetriveViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ("get",)


class IngredientViewSet(ListRetriveViewSet):
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    queryset = Ingredient.objects.all()
    http_method_names = ("get",)


class RecipeViewSet(ModelViewSet):
    pagination_class=PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class=(RecipeFilter)
    queryset = Recipe.objects.all()
    http_method_names = ("get", "post", "put", "patch", "delete",)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return PostRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = GetRecipeSerializer(
            instance=serializer.instance,
            context={"request": self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = GetRecipeSerializer(
            instance=serializer.instance,
            context={"request": self.request},
        )
        return Response(
            serializer.data, status=HTTP_200_OK
        )

    def add_to_favorite(self, request, recipe):
        try:
            Favorites.objects.create(user=request.user, favorit_recipe=recipe)
        except IntegrityError:
            return Response(
                {"errors": "Уже добавлено в избранное"},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = FavoritRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def delete_from_favorite(self, request, recipe):
        favorite = Favorites.objects.filter(
            user=request.user,
            favorit_recipe=recipe
        )
        if not favorite.exists():
            return Response(
                {"errors": "Такого рецерта нет в избранном"},
                status=HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=("post", "delete",),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)
