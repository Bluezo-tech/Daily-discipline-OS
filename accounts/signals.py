from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    """Create superuser automatically after migrations."""
    if sender.name == 'accounts':
        email = settings.ADMIN_EMAIL
        password = settings.ADMIN_PASSWORD
        
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            print(f"\n{'='*50}")
            print(f"Superuser created successfully!")
            print(f"Email: {email}")
            print(f"Password: {'*' * len(password)}")
            print(f"{'='*50}\n")