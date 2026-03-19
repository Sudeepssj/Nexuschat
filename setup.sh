#!/bin/bash
# NexusChat - Quick Setup Script
# Run this once to set everything up

echo "🚀 Setting up NexusChat..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install Django==4.2.7 channels==4.0.0 daphne==4.0.0

# Run migrations
python manage.py makemigrations chat
python manage.py migrate

# Create superuser (optional - will prompt)
echo ""
echo "Create admin user (optional, press Ctrl+C to skip):"
python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || true

# Collect static files
python manage.py collectstatic --noinput 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "▶  To run the server:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Then open: http://127.0.0.1:8000"
echo "👤 Register at: http://127.0.0.1:8000/register/"
echo "🔧 Admin at:    http://127.0.0.1:8000/admin/"
