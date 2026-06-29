Daily Discipline OSA professional-grade productivity system designed to foster consistency. Features include task management, habit tracking, streak counters, achievement badges, and real-time notifications—fully optimized as a Progressive Web App (PWA).FeaturesAuthentication: Email-based registration and login with secure password handling.Profile Management: Edit profile, upload avatar, and manage account settings.Daily Tasks: Create, track, and manage responsibilities with reminders.Habit Tracker: Build discipline with streak-based check-ins.Gamification: Badge system for tracking streaks, tasks, and habits.Notifications: Admin announcements and automated user reminders.Dashboard: Visual productivity statistics using Chart.js.Custom Admin: Advanced management interface for users and data.PWA Ready: Installable on mobile and desktop for a native experience.Tech StackBackend: Django 5.0+ (Python 3.10+)Database: PostgreSQL (Production) / SQLite (Development)Frontend: Django Templates, Tailwind CSS, Chart.jsPWA: Service Worker & Web ManifestQuick Start1. InstallationBashpip install -r requirements.txt
2. ConfigurationBashcp .env.example .env
# Edit the .env file with your specific settings (SECRET_KEY, Database, etc.)
3. Database & ServerBashpython manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Access the application at http://127.0.0.1:8000/ once the server is running.Project StructurePlaintextdaily_discipline_os/
├── daily_discipline_os/      # Project settings
├── accounts/                  # Auth and user profiles
├── tasks/                     # Task management logic
├── habits/                    # Habit tracking
├── achievements/              # Badge logic
├── notifications/             # Alert system
├── dashboard/                 # Analytics and charts
├── templates/                 # HTML UI components
└── static/                    # CSS, JS, and PWA assets
Deployment NotesTo ensure your application runs correctly in production:Static Files: Always run python manage.py collectstatic to ensure your CSS and PWA files are served.Environment Variables: Never commit your .env file to version control.Admin Access: Access your custom dashboard at /admin/ after running migrations and creating a superuser.LicenseThis project is for personal use.Built by Bluezo Tech | Powered by Ugo-Codes
