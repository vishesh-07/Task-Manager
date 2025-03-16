# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # If task_id is provided (for updates), it will be added to the group name
        self.task_id = self.scope['url_route']['kwargs'].get('task_id', None)
        
        if self.task_id:
            self.room_group_name = f'task_{self.task_id}'  # For updates, specific task group
        else:
            self.room_group_name = 'tasks'  # For creation, general task group

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle the message received from the WebSocket client
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Send message to WebSocket
    async def send_task_update(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
