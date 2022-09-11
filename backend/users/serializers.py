from django.contrib.auth.hashers import make_password
from recipes.models import Recipe
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer
)

from .models import User


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name",
            "last_name", "password", "is_subscribed",)
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
        }

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )

    def create(self, validated_data):
        validated_data["password"] = (
            make_password(validated_data.pop("password"))
        )
        return super().create(validated_data)

class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]

class FavoritRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time",)


class FollowSerializer(AuthorSerializer):
    recipes = FavoritRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ("recipes", "recipes_count",)

    def get_recipes_count(self, obj):
        return obj.recipes.count()
