# tasks/routing.py
from django.urls import path
from .consumers import TaskConsumer

websocket_urlpatterns = [
    path('ws/tasks/', TaskConsumer.as_asgi()),
    path('ws/tasks/<int:task_id>/', TaskConsumer.as_asgi()),  # Ensure this matches the URL you're using
]
