from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Create default roles and permissions'

    def handle(self, *args, **options):
        # Create default admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hpb-registry.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')  # Change this after first login!
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Ensure admin has admin role
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        if not created and admin_profile.role != 'admin':
            admin_profile.role = 'admin'
            admin_profile.save()
            self.stdout.write('Updated admin role')
        
        self.stdout.write(self.style.SUCCESS('Roles setup complete!'))
