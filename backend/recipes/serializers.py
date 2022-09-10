from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes import models
from rest_framework import serializers
from users.models import ShoppingCart
from users.serializers import AuthorSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ("id", "name", "measurement_unit")


class GetIngredientRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.IngredientRecipe
        fields = ("id", "name",  "measurement_unit")


class PostIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IngredientRecipe
        fields = ("id", "quantity")


class GetIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
        )

    class Meta:
        model = models.IngredientRecipe
        fields = ("id", "name", "measurement_unit", "quantity")


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer()
    ingredients = GetIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = models.Recipe
        fields = (
            "id", "name", "tags", "author", "ingredients", "is_favorited",
            "is_in_shopping_cart", "image", "text", "cooking_time"
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return (user.is_authenticated and user.client.filter(
            favorit_recipe=obj).exists()
            )

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        try:
            return (
                user.is_authenticated and
                user.shopping_cart.recipes.filter(pk__in=(obj.pk,)).exists()
            )
        except ShoppingCart.DoesNotExist:
            return False


class PostRecipeSerializer(serializers.ModelSerializer):
    ingredients = PostIngredientSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field="id",
            queryset=models.Tag.objects.all(),
        ),
    )
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            "ingredients", "tags", "image", "name", "text", "cooking_time",
        )

    def validate(self, attrs):
        if attrs['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше одной минуты!')
        if len(attrs['tags']) == 0:
            raise serializers.ValidationError(
                'Рецепт не может быть без тегов!')
        if len(attrs['tags']) > len(set(attrs['tags'])):
            raise serializers.ValidationError(
                'Теги не могут повторяться!')
        if len(attrs['ingredients']) == 0:
            raise serializers.ValidationError(
                'Без ингредиентов рецепта не бывает!')
        for ingredient in attrs['ingredients']:
            if ingredient['quantity'] < 1:
                raise serializers.ValidationError(
                     'Количество ингредиента не может быть меньше 1!'
                    )
        return attrs

    def add_ingredients_and_tags(self, instance, validated_data):
        ingredients, tags = (
            self.context["request"].data['ingredients'], validated_data.pop(
                'tags')
        )
        for ingredient in ingredients:
            quantity_of_ingredient, _ = (
                models.IngredientRecipe.objects.get_or_create(
                    ingredient=get_object_or_404(
                        models.Ingredient,
                        id=ingredient['id'],
                    ),
                    quantity=ingredient['quantity'],)
                )
            instance.ingredients.add(quantity_of_ingredient)
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def create(self, validated_data):
        saved = {}
        saved["ingredients"] = validated_data.pop("ingredients")
        saved["tags"] = validated_data.pop("tags")
        recipe = models.Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(recipe, saved)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance = self.add_ingredients_and_tags(instance, validated_data)
        return super().update(instance, validated_data)
