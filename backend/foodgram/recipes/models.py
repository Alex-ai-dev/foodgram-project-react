from distutils.command.upload import upload
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name= models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=50)


class Tag(models.Model):
    name= models.CharField(max_length=200, unique=True)
    color= models.CharField(max_length=7, unique=True)
    slug= models.SlugField(max_length=200, unique=True)

class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name='unique_follow')
        ]
        
class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200
    )
    text = models.TextField()
    tags=models.ManyToManyField(
        Tag, verbose_name="Теги"
    )
    pub_date= models.DateTimeField(
        auto_now_add=True
    )
    image = models.ImageField(upload_to='recipes/')
    cooking_time= models.PositiveIntegerField()
    ingredients = models.ManyToManyField(Ingredient, verbose_name='Ингредиенты')


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete= models.CASCADE, related_name='IngredientRecipe')
    quantity= models.PositiveIntegerField()


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client',
        verbose_name='Пользователь',
    )   
    favorit_recipe= models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorit_recipes',
        verbose_name='Избранные рецепты'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['favourit_recipe', 'user'], name='unique_favourite')
        ]

class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Пользователь',
    )
    buy_recipe= models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_buy',
        verbose_name='Рецепт в корзине покупок')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['buy_recipe', 'user'], name='unique_buy_recipe')
        ]
