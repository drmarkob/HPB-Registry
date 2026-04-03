import os
import shutil
import gzip
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = 'Backup the database and media files with retention policy'
    
    def add_arguments(self, parser):
        parser.add_argument('--compress', action='store_true', help='Compress backup with gzip')
        parser.add_argument('--retention-days', type=int, default=30, help='Days to keep backups')
        parser.add_argument('--no-media', action='store_true', help='Skip media files backup')
    
    def handle(self, *args, **options):
        compress = options['compress']
        retention_days = options['retention_days']
        backup_media = not options['no_media']
        
        # Create backup directory
        backup_dir = os.path.join(settings.BASE_DIR, '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup database (JSON format)
        db_backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.json')
        self.stdout.write(f'Backing up database to {db_backup_file}...')
        call_command('dumpdata', output=db_backup_file)
        
        # For SQLite, also copy the file
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            db_file = settings.DATABASES['default']['NAME']
            if os.path.exists(db_file):
                sqlite_backup = os.path.join(backup_dir, f'db_{timestamp}.sqlite3')
                shutil.copy2(db_file, sqlite_backup)
                self.stdout.write(f'Copied SQLite database to {sqlite_backup}')
                
                if compress:
                    compressed_file = f'{sqlite_backup}.gz'
                    with open(sqlite_backup, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(sqlite_backup)
                    self.stdout.write(f'Compressed: {compressed_file}')
        
        # Backup media files
        if backup_media:
            media_dir = settings.MEDIA_ROOT
            if os.path.exists(media_dir):
                media_backup = os.path.join(backup_dir, f'media_{timestamp}.zip')
                self.stdout.write(f'Backing up media files to {media_backup}...')
                shutil.make_archive(media_backup.replace('.zip', ''), 'zip', media_dir)
        
        # Clean old backups
        cutoff = datetime.now() - timedelta(days=retention_days)
        removed = 0
        
        for file in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff:
                    os.remove(file_path)
                    removed += 1
        
        if removed:
            self.stdout.write(f'Removed {removed} old backup(s) (older than {retention_days} days)')
        
        self.stdout.write(self.style.SUCCESS(f'Backup completed successfully!'))
