# Daily Discipline OS

A professional personal productivity system with daily tasks, habit tracking, streaks, achievements, notifications, and PWA support.

## Features

- **Authentication**: Email-based registration and login with secure password handling
- **Profile Management**: Edit profile, upload avatar, change password
- **Daily Tasks**: Create, manage, and track tasks with due dates, times, and reminders
- **Task Reminders**: Optional reminders with browser notifications and alarm sounds
- **Habit Tracker**: Build streaks with daily check-ins for your habits
- **Achievements**: Badge system with streak, task, and habit achievements
- **Notifications**: Admin announcements and user notifications (missed tasks, reminders)
- **Dashboard**: Visual overview with Chart.js statistics
- **Dark Mode**: Toggle between light and dark themes (persisted per user)
- **PWA Support**: Installable on Android and Desktop with offline caching
- **Admin Panel**: Manage users, view data, send notifications

## Tech Stack

- **Backend**: Django 5.0+ with Python 3.10+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Django Templates + Tailwind CSS + Chart.js
- **Authentication**: Django's built-in session-based authentication
- **PWA**: Service Worker + Web Manifest

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **App**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

**Default Admin Credentials:**
- Email: `Ugodesktop@gmail.com`
- Password: `enzo@738319`

---

## Windows Setup

### Prerequisites

1. **Install Python 3.10+**
   - Download from: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Install PostgreSQL** (optional, for production)
   - Download from: https://www.postgresql.org/download/windows/

### Setup Steps

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env

# Edit .env with your settings (SQLite for development)
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser (optional - auto-created from env)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## Project Structure

```
daily_discipline_os/
├── daily_discipline_os/      # Main project settings
├── accounts/                  # User authentication & profiles
├── tasks/                     # Task management with reminders
├── habits/                    # Habit tracking with streaks
├── achievements/              # Badge/achievement system
├── notifications/             # Notification system
├── dashboard/                 # Main dashboard with charts
├── templates/                 # HTML templates
├── static/                    # Static files (CSS, JS, PWA)
│   ├── css/styles.css
│   ├── js/app.js
│   ├── manifest.webmanifest
│   └── sw.js
├── manage.py
├── requirements.txt
└── README.md
```

---

## PWA Installation

The app is installable as a Progressive Web App:

1. Open the app in Chrome (Desktop or Android)
2. Click the "Install App" button that appears
3. Or use the browser's install prompt
4. The app will be added to your home screen/launcher

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_ENGINE` | Database engine | `django.db.backends.sqlite3` |
| `DB_NAME` | Database name | `db.sqlite3` |
| `DB_USER` | Database user | - |
| `DB_PASSWORD` | Database password | - |
| `DB_HOST` | Database host | - |
| `DB_PORT` | Database port | - |
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `ADMIN_EMAIL` | Auto-created admin email | `Ugodesktop@gmail.com` |
| `ADMIN_PASSWORD` | Auto-created admin password | `enzo@738319` |

---

## URL Namespaces

- `accounts:` - Authentication (login, register, profile)
- `tasks:` - Task management
- `habits:` - Habit tracking
- `achievements:` - Achievements
- `notifications:` - Notifications
- `dashboard:` - Dashboard
- `admin_panel:` - Admin control panel

---

## License

This project is for personal use.

**Powered by Bluezo-Tech**