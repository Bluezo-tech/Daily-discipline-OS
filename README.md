Daily Discipline OSA professional-grade productivity system designed to foster consistency. Features include task management, habit tracking, streak counters, achievement badges, and real-time notifications—fully optimized as a Progressive Web App (PWA).FeaturesSecure Authentication: Email-based registration with industry-standard password hashing.Task Management: Organize daily responsibilities with custom reminders and alarm triggers.Habit Tracking: Build long-term discipline with streak-based tracking and check-ins.Gamification: Unlock badges and achievements based on your progress.Admin Control: Manage users and broadcast notifications via the Custom Admin Dashboard.PWA Optimized: Fully installable on mobile and desktop for a native-app experience.Theme Support: Seamless toggle between light and dark modes.Tech StackBackend: Django 5.0+ (Python 3.10+)Database: PostgreSQL (Production) / SQLite (Development)Frontend: Tailwind CSS, Chart.js, and Django TemplatesPWA: Service Workers and Web Manifest for offline capabilityQuick Start1. Setup EnvironmentBash# Clone the repository
git clone https://github.com/Bluezo-tech/Daily-discipline-OS.git
cd Daily-discipline-OS

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
2. ConfigurationCreate your environment variables from the template:Bashcopy .env.example .env
Open the .env file and update your database settings and SECRET_KEY accordingly.3. Initialize DatabaseBashpython manage.py migrate
python manage.py createsuperuser
4. Run the ServerBashpython manage.py runserver
Access the application at http://127.0.0.1:8000/ and the admin panel at http://127.0.0.1:8000/admin/.Environment VariablesEnsure the following variables are configured in your .env file:VariableDescriptionSECRET_KEYYour unique Django secret keyDEBUGSet to False for productionDB_ENGINEDatabase driver (e.g., django.db.backends.postgresql)ADMIN_EMAILAdmin contact for system notificationsNote: Never commit your .env file to version control.Deployment NotesFor production environments, ensure you collect static files to serve CSS and JavaScript correctly:Bashpython manage.py collectstatic
LicenseThis project is for personal use.Built by Bluezo Tech | Powered by Ugo-Codes
