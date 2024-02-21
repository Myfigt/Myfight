"""
ASGI config for myfight project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from api.consumers import RealtimeDataConsumer
from api.chatconsumers import ChatConsumer
from api.friend_requests_consumers import FriendRequestsConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myfight.settings")

application = get_asgi_application()

websocket_urlpatterns = [
    path("ws/data/", RealtimeDataConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    # re_path(
    #     r"ws/friends/(?P<user_id>\w+)/(?P<friend_id>\w+)/$",
    #     FriendRequestsConsumer.as_asgi(),
    # ),
    re_path(
        r"ws/friends/(?P<user_id>\w+)/$",
        FriendRequestsConsumer.as_asgi(),
    ),
]

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
