from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_color = models.CharField(max_length=7, default='#6C63FF')
    bio = models.TextField(blank=True, max_length=200)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def avatar_initials(self):
        name = self.user.get_full_name() or self.user.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper()


class Room(models.Model):
    ROOM_TYPES = (('direct', 'Direct Message'), ('group', 'Group Chat'))
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='group')
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def last_message(self):
        return self.messages.order_by('-timestamp').first()

    @property
    def member_count(self):
        return self.members.count()


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
