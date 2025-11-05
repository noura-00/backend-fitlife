from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check existing users in the database'

    def handle(self, *args, **options):
        users = User.objects.all()
        count = users.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Total Users: {count} ===\n'))
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No users found in the database.'))
            self.stdout.write(self.style.WARNING('You can create a user by:'))
            self.stdout.write(self.style.WARNING('  1. Using the signup form on the website'))
            self.stdout.write(self.style.WARNING('  2. Running: python manage.py createsuperuser'))
            self.stdout.write(self.style.WARNING('  3. Using: python manage.py shell to create a user programmatically\n'))
        else:
            for user in users:
                self.stdout.write(f'Username: {self.style.SUCCESS(user.username)}')
                self.stdout.write(f'  Email: {user.email or "Not set"}')
                self.stdout.write(f'  Active: {"Yes" if user.is_active else "No"}')
                self.stdout.write(f'  Date Joined: {user.date_joined}')
                self.stdout.write(f'  Is Staff: {"Yes" if user.is_staff else "No"}')
                self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('=' * 50))




