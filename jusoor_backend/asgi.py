"""
ASGI config for jusoor_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jusoor_backend.settings')

django_asgi_app = get_asgi_application()
from authentication.middleware import JWTAuthMiddlewareStack

import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'wss': AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    )
    # Just HTTP for now. (We can add other protocols later.)
})
