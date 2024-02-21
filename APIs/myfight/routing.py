# routing.py

from django.urls import re_path
from api.consumers import RealtimeDataConsumer

websocket_urlpatterns = [
    re_path(r"ws/realtime/$", RealtimeDataConsumer.as_asgi()),
]
