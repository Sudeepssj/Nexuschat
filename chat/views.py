from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.http import require_POST
import json, random
from .models import Room, Message, UserProfile, Notification
from .forms import RegisterForm, RoomForm


AVATAR_COLORS = [
    '#6C63FF', '#FF6584', '#43D9AD', '#FFB547',
    '#4ECDC4', '#FF6B6B', '#A8EDEA', '#FED9B7',
]


def get_or_create_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        profile.avatar_color = random.choice(AVATAR_COLORS)
        profile.save()
    return profile


@login_required
def index(request):
    rooms = Room.objects.filter(members=request.user).order_by('-created_at')
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    profile = get_or_create_profile(request.user)
    return render(request, 'chat/index.html', {
        'rooms': rooms,
        'users': users,
        'unread_count': unread_count,
        'profile': profile,
    })


@login_required
def room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    if request.user not in room.members.all():
        room.members.add(request.user)
    messages = room.messages.select_related('author', 'author__profile').order_by('timestamp')
    members = room.members.select_related('profile').all()
    profile = get_or_create_profile(request.user)
    Notification.objects.filter(user=request.user, message__room=room, is_read=False).update(is_read=True)
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages,
        'members': members,
        'profile': profile,
    })


@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            base_slug = slugify(room.name)
            slug = base_slug
            counter = 1
            while Room.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            room.slug = slug
            room.save()
            room.members.add(request.user)
            for uid in request.POST.getlist('members'):
                try:
                    u = User.objects.get(id=uid)
                    room.members.add(u)
                except User.DoesNotExist:
                    pass
            return redirect('room', slug=room.slug)
    else:
        form = RoomForm()
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/create_room.html', {'form': form, 'users': users})


@login_required
def direct_message(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    ids = sorted([request.user.id, other_user.id])
    slug = f'dm-{ids[0]}-{ids[1]}'
    room, created = Room.objects.get_or_create(
        slug=slug,
        defaults={
            'name': f'{request.user.username} & {other_user.username}',
            'room_type': 'direct',
            'created_by': request.user,
        }
    )
    if created:
        room.members.add(request.user, other_user)
    return redirect('room', slug=room.slug)


@login_required
def search(request):
    q = request.GET.get('q', '').strip()
    results = {'rooms': [], 'users': []}
    if q:
        rooms = Room.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q),
            members=request.user
        )[:5]
        users = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
        ).exclude(id=request.user.id)[:5]
        results['rooms'] = [{'id': r.id, 'name': r.name, 'slug': r.slug, 'type': r.room_type} for r in rooms]
        results['users'] = [{'id': u.id, 'username': u.username} for u in users]
    return JsonResponse(results)


@login_required
def notifications(request):
    # Mark as read BEFORE slicing
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    notifs = Notification.objects.filter(user=request.user).select_related('message__author', 'message__room')[:20]
    return render(request, 'chat/notifications.html', {'notifications': notifs})


@login_required
def api_notifications(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = UserProfile.objects.create(
                user=user,
                avatar_color=random.choice(AVATAR_COLORS)
            )
            login(request, user)
            # Create a welcome room
            welcome, _ = Room.objects.get_or_create(
                slug='general',
                defaults={'name': 'General', 'room_type': 'group', 'created_by': user, 'description': 'Welcome to the chat!'}
            )
            welcome.members.add(user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
