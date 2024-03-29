from django.db import IntegrityError
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, UserViewSet
from recipes.models import Recipe
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)
from rest_framework.viewsets import GenericViewSet

from foodgram.pagination import PageLimitPagination

from .models import Follow, ShoppingCart, User
from .serializers import (FavoritRecipeSerializer,
                          FollowSerializer)

FILE_NAME = "shopping_cart.txt"


class TokenCreateWithCheckBlockStatusView(TokenCreateView):
    def _action(self, serializer):
        return super()._action(serializer)


class UserFollowViewSet(UserViewSet):
    pagination_class = PageLimitPagination
    lookup_url_kwarg = "user_id"

    def get_subscribtion_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        return FollowSerializer(*args, **kwargs)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        self.get_serializer
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_subscribtion_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_subscribtion_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def create_Follow(self, request, author):
        if request.user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя!"},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            Subscribe = Follow.objects.create(
                user=request.user,
                author=author,
            )
        except IntegrityError:
            return Response(
                {"errors": "Нельзя подписаться дважды!"},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_subscribtion_serializer(Subscribe.author)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_Follow(self, request, author):
        try:
            Follow.objects.get(user=request.user, author=author).delete()
        except Follow.DoesNotExist:
            return Response(
                {
                    "errors":
                    "Нельзя отписаться от данного пользователя,"
                    "если вы не подписаны на него!"
                },
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(
            status=HTTP_204_NO_CONTENT
        )

    @action(
        methods=("POST", "delete",),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, user_id=None):
        try:
            author = get_object_or_404(User, pk=user_id)
        except Http404:
            return Response(
                {"detail": "Пользователь не найден!"},
                status=HTTP_404_NOT_FOUND,
            )
        if request.method == "POST":
            return self.create_Follow(request, author)
        return self.delete_Follow(request, author)


class ShoppingCartViewSet(GenericViewSet):
    NAME = "ingredients__ingredient__name"
    MEASUREMENT_UNIT = "ingredients__ingredient__measurement_unit"
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoritRecipeSerializer
    queryset = ShoppingCart.objects.all()
    http_method_names = ("get", "post", "delete",)

    def generate_shopping_cart_data(self, request):
        recipes = (
            request.user.shopping_cart.recipes.prefetch_related("ingredients")
        )
        return (
            recipes.order_by(self.NAME)
            .values(self.NAME, self.MEASUREMENT_UNIT)
            .annotate(total=Sum("ingredients__amount"))
        )

    def generate_ingredients_content(self, ingredients):
        content = ""
        for ingredient in ingredients:
            content += (
                f"{ingredient[self.NAME]}"
                f" ({ingredient[self.MEASUREMENT_UNIT]})"
                f" — {ingredient['total']}\r\n"
            )
        return content

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request):
        try:
            ingredients = self.generate_shopping_cart_data(request)
        except ShoppingCart.DoesNotExist:
            return Response(
                {"errors": "Список покупок не существует!"},
                status=HTTP_400_BAD_REQUEST
            )
        content = self.generate_ingredients_content(ingredients)
        response = HttpResponse(
            content, content_type="text/plain,charset=utf8"
        )
        response["Content-Disposition"] = f"attachment; filename={FILE_NAME}"
        return response

    def add_to_shopping_cart(self, request, recipe, shopping_cart):
        if shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {"errors": "Рецепт уже добавлен!"},
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipes.add(recipe)
        serializer = self.get_serializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def remove_from_shopping_cart(self, request, recipe, shopping_cart):
        if not shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {
                    "errors":
                    "Нельзя удалить рецепт из списка покупок,"
                    "которого нет в списке покупок!"
                },
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipes.remove(recipe)
        return Response(
            status=HTTP_204_NO_CONTENT,
        )

    @action(methods=("post", "delete",), detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = (
            ShoppingCart.objects.get_or_create(user=request.user)[0]
        )
        if request.method == "POST":
            return self.add_to_shopping_cart(request, recipe, shopping_cart)
        return self.remove_from_shopping_cart(request, recipe, shopping_cart)
