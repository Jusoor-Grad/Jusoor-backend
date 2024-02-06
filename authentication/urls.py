
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import AuthViewset, TokenViewset, UserViewset

router = SimpleRouter()

router.register('auth', AuthViewset, basename='auth')
router.register('tokens', TokenViewset, basename='tokens')
router.register('users', UserViewset, basename='users')



urlpatterns = [
    *router.urls,
]