from django.urls import include, path
from djoser.views import TokenDestroyView, TokenCreateView
from rest_framework.routers import DefaultRouter

from .views import (ShoppingCartViewSet, TokenCreateWithCheckBlockStatusView,
                    UserFollowViewSet)

router = DefaultRouter()
router.register(r"users", UserFollowViewSet, basename="users")
router.register(r"recipes", ShoppingCartViewSet, basename="shopping_cart")

app_name = "users"

authorization = [
    path(
        "token/login/",
        TokenCreateView.as_view(),
        name="login",
    ),
    path("token/logout/", TokenDestroyView.as_view(), name="logout"),
]

urlpatterns = [
    path("auth/", include(authorization)),
    path("", include(router.urls)),
]
