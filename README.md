# 💬 NexusChat — Real-Time Chat Application

A full-stack Django real-time chat application with WebSocket support, dark modern UI, and all the features you need.

---

## ✨ Features

- **Real-time messaging** via WebSockets (Django Channels)
- **One-to-one & group chats** — direct messages and rooms
- **Live typing indicators** — see when someone is typing
- **Online/offline presence** — real-time status updates
- **Notifications** — get notified of new messages
- **Live search** — search rooms and users with jQuery
- **User authentication** — register, login, logout
- **Dark modern UI** — custom design with Bootstrap + Tailwind-inspired CSS
- **Responsive layout** — works on desktop and tablet
- **SQLite database** — no external DB setup needed
- **Admin dashboard** — manage users, rooms, and messages

---

## 🗂 Project Structure

```
chatapp/
├── chatapp/
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL config
│   ├── asgi.py           # ASGI + WebSocket config
│   └── wsgi.py
├── chat/
│   ├── models.py         # UserProfile, Room, Message, Notification
│   ├── consumers.py      # WebSocket consumers (ChatConsumer, PresenceConsumer)
│   ├── routing.py        # WebSocket URL routing
│   ├── views.py          # Django views
│   ├── forms.py          # Register & Room forms
│   ├── urls.py           # HTTP URL patterns
│   ├── admin.py          # Admin config
│   └── signals.py        # Auto-create user profiles
├── templates/
│   ├── base.html         # Base layout with nav rail + sidebar
│   ├── chat/
│   │   ├── index.html        # Dashboard / welcome
│   │   ├── room.html         # Chat room (main UI)
│   │   ├── create_room.html  # Create new room
│   │   └── notifications.html
│   └── registration/
│       ├── login.html
│       └── register.html
├── requirements.txt
├── setup.sh              # Quick setup script
└── manage.py
```

---

## 🚀 Quick Start

### Option A — Automatic Setup (Linux/Mac)

```bash
cd chatapp
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python manage.py runserver
```

### Option B — Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# or: venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install Django==4.2.7 channels==4.0.0 daphne==4.0.0

# 3. Run migrations
python manage.py makemigrations chat
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Start the server
python manage.py runserver
```

### 6. Open in browser

| URL | Page |
|-----|------|
| http://127.0.0.1:8000/register/ | Create account |
| http://127.0.0.1:8000/login/ | Sign in |
| http://127.0.0.1:8000/ | Dashboard |
| http://127.0.0.1:8000/admin/ | Admin panel |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Real-time | Django Channels 4.0 (WebSockets) |
| Database | SQLite |
| Frontend | HTML, CSS, Bootstrap 5, jQuery |
| Font | Syne (display) + Inter (body) |
| Server | Daphne (ASGI) |

---

## 🔌 How WebSockets Work

```
Browser ──WS connect──► Django Channels (ASGI)
                              │
                    ChatConsumer.connect()
                              │
                    group_add(room_group)
                              │
Browser ──send message──► receive() ──► save to DB
                              │
                    group_send(room_group)
                              │
         All room members ◄── chat_message()
```

- Uses **InMemoryChannelLayer** (no Redis needed for development)
- For production, swap to **RedisChannelLayer**: `pip install channels-redis`

---

## 🎨 UI Highlights

- Custom dark theme with CSS variables
- Syne display font + Inter body
- Smooth message animations
- Collapsible members panel
- Live typing indicator
- Toast notifications
- Ambient background orbs on auth pages

---

## 🔧 VS Code Setup

Install these extensions for the best experience:
- **Python** (Microsoft)
- **Django** (Baptiste Darthenay)
- **Pylance**
- **SQLite Viewer**

Set your Python interpreter to the venv:
`Ctrl+Shift+P` → "Python: Select Interpreter" → choose `./venv/bin/python`

---

## 📦 Production Notes

1. Set `DEBUG = False` in `settings.py`
2. Add your domain to `ALLOWED_HOSTS`
3. Change `SECRET_KEY` to a random value
4. Use Redis for channel layer: `pip install channels-redis`
5. Run with Daphne: `daphne -b 0.0.0.0 -p 8000 chatapp.asgi:application`
