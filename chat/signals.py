from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile
import random

AVATAR_COLORS = ['#6C63FF','#FF6584','#43D9AD','#FFB547','#4ECDC4','#FF6B6B']

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'avatar_color': random.choice(AVATAR_COLORS)}
        )
