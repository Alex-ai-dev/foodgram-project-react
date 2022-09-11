from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    email = models.EmailField(
        verbose_name="E-mail",
        unique=True,
        max_length=254,
        blank=False
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    USERNAME_FIELD = 'email'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("author_id",)
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_follow")
        ]

    def __str__(self):
        return f"{self.user} -> {self.author}"


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        unique=True,
    )
    recipes = models.ManyToManyField(
        'recipes.Recipe',
        related_name='in_shopping_cart',
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = "Продукт в корзине"
        verbose_name_plural = "Продукты в корзине"

    def __str__(self):
        return f"{self.user}"
