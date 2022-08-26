from backend.foodgram.recipes.models import Follow, Tag
from recipes import models
from rest_framework import serializers
from users.models import User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'count', 'measurement_unit')


class FollowSerializer(serializers.ModelSerializer):
    
    author = serializers.SlugRelatedField(
        read_only='True',
        slug_field='username'
    )
    user = serializers.SlugRelatedField(
        read_only='True',
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        fields = ('author', 'user')
        model = Follow