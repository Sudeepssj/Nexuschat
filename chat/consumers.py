import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Room, Message, UserProfile, Notification
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.set_user_online(True)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user': self.user.username,
                'status': 'online',
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.set_user_online(False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user': self.user.username,
                    'status': 'offline',
                }
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            content = data.get('message', '').strip()
            if not content:
                return
            message = await self.save_message(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': content,
                    'username': self.user.username,
                    'user_id': self.user.id,
                    'message_id': message.id,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'avatar_color': await self.get_avatar_color(),
                    'initials': await self.get_initials(),
                }
            )
        elif msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': self.user.username,
                    'is_typing': data.get('is_typing', False),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
            'avatar_color': event['avatar_color'],
            'initials': event['initials'],
            'is_own': event['user_id'] == self.user.id,
        }))

    async def typing_indicator(self, event):
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user': event['user'],
            'status': event['status'],
        }))

    @database_sync_to_async
    def save_message(self, content):
        room = Room.objects.get(slug=self.room_slug)
        msg = Message.objects.create(room=room, author=self.user, content=content)
        for member in room.members.exclude(id=self.user.id):
            Notification.objects.create(user=member, message=msg)
        return msg

    @database_sync_to_async
    def set_user_online(self, status):
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.is_online = status
        profile.last_seen = timezone.now()
        profile.save()

    @database_sync_to_async
    def get_avatar_color(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        return profile.avatar_color

    @database_sync_to_async
    def get_initials(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        return profile.avatar_initials


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = 'presence'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.set_online(True)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'presence_update',
            'user': self.user.username,
            'status': 'online',
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.set_online(False)
            await self.channel_layer.group_send(self.group_name, {
                'type': 'presence_update',
                'user': self.user.username,
                'status': 'offline',
            })
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def presence_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def receive(self, text_data):
        pass

    @database_sync_to_async
    def set_online(self, status):
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.is_online = status
        profile.last_seen = timezone.now()
        profile.save()
