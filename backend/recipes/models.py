from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=50, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}"


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name="Название тега"
    )
    color = models.CharField(
        max_length=7, unique=True, verbose_name="Цвет в HEX"
    )
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"{self.name}"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE, related_name="IngredientRecipe",
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.amount}"
            f" ({self.ingredient.measurement_unit})"
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True,
        related_name="recipes",
        verbose_name="Автор"
    )
    name = models.CharField(
        max_length=200, verbose_name="Название"
    )
    text = models.TextField(verbose_name="Описание")
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
        validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        IngredientRecipe, verbose_name="Ингредиенты"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.name} ({self.author})"


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client",
        verbose_name="Пользователь",
    )
    favorit_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorit_recipes",
        verbose_name="Избранные рецепты"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["favorit_recipe", "user"], name="unique_favourite")
        ]

    def __str__(self):
        return f"{self.user} -> {self.recipe}"
