# clinical/management/commands/backup_db.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Backup the database and media files'

    def handle(self, *args, **options):
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup database
        db_backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.json')
        self.stdout.write(f'Backing up database to {db_backup_file}...')
        call_command('dumpdata', output=db_backup_file)
        
        # For SQLite, also copy the file
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            db_file = settings.DATABASES['default']['NAME']
            if os.path.exists(db_file):
                import shutil
                sqlite_backup = os.path.join(backup_dir, f'db_{timestamp}.sqlite3')
                shutil.copy2(db_file, sqlite_backup)
                self.stdout.write(f'Copied SQLite database to {sqlite_backup}')
        
        self.stdout.write(self.style.SUCCESS(f'Backup completed successfully!'))
