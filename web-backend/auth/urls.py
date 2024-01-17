from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from auth.views import AuthView

router = SimpleRouter()

router.register('', AuthView, basename='actions')

from auth.views import AuthView

urlpatterns = [
    *router.urls,
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]