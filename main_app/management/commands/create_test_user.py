from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a test user for login testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for the test user (default: testuser)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='test123',
            help='Password for the test user (default: test123)',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f'{username}@example.com'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created test user!\n'
                f'Username: {username}\n'
                f'Password: {password}\n'
                f'You can now login with these credentials.\n'
            )
        )




