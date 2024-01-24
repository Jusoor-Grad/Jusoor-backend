
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser, User
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db import close_old_connections
import jwt
from channels.auth import AuthMiddlewareStack
from jusoor_backend.settings import env, SIMPLE_JWT
from authentication.placeholders import SIMPLE_JWT_SIGNING_KEY
import re

@database_sync_to_async
def get_user(validated_token: str):

    try:
        user = User.objects.get(id=validated_token['user_id'])
        
        return user
    except User.DoesNotExist:
        print(f'User does not exist')
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """ Custom Middleware to use stateless JWT tokens for
    authenticating WebSocket connections"""

    def __init__(self, app):
        # storing the ASGI app instance inside the class object
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # closing all old database connections to prevent using time out connections
        close_old_connections()
    

        # get token form the WebSocket security protocol header
        print((scope['headers']))
        token = re.split(r'\s*,\s*', (dict(scope['headers'])[b'sec-websocket-protocol']).decode('utf-8'))[1]
        
        dict(scope['headers']).pop(b'sec-websocket-protocol')
        try:
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            print('Invalid token')
            return None
        else:

            decoded_data = jwt.decode(token, env(SIMPLE_JWT_SIGNING_KEY), algorithms = [SIMPLE_JWT['ALGORITHM']]  )
            print(decoded_data)
            scope['user'] = await get_user(validated_token=decoded_data)
        return await self.app(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """ Wrapper for websocket url routing"""
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))