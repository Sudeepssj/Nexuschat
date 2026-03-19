from django.contrib import admin
from .models import Room, Message, UserProfile, Notification

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'room_type', 'member_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'room', 'content', 'timestamp']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_seen']

admin.site.register(Notification)
