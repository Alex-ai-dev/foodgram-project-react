from django.contrib.admin import ModelAdmin, display, register
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Sum

from .models import Follow, ShoppingCart, User


@register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = (
        "id", "email", "username", "first_name", "last_name",
        "is_superuser",
    )
    list_filter = (
        "email", "username", "is_superuser",
    )
    search_fields = ("email", "username", "first_name", "last_name",)
    ordering = ("id", "email", "username",)


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ("user", "author",)
    empty_value_display = "< Тут Пусто >"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ("user", "count_ingredients",)
    readonly_fields = ("count_ingredients",)
    empty_value_display = "< Тут Пусто >"

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    @display(description="Количество ингредиентов")
    def count_ingredients(self, obj):
        return (
            obj.recipes.all().annotate(count_ingredients=Count("ingredients"))
            .aggregate(total=Sum("count_ingredients"))["total"]
        )
