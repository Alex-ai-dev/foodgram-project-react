from backend.foodgram.recipes import models
from rest_framework import serializers
from users.models import User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient 
        fields = ('id', 'name',  'measurement_unit')


class PostIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IngredientRecipe
        fields = ('id', 'quantity')

class GetIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    class Meta:
        model = models.IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer()
    ingredients = GetIngredientSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    class Meta:
        model = models.Recipe
        fields = (
            'id', 'name', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'image', 'text', 'cooking_time'
        )
        def get_is_favorited(self, obj):
            user = self.context['request'].user
            return (user.is_authenticated and user.favorit_recipes.filter(favorit_recipes = obj).exists())
















"""
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
        model = models.Follow
"""
