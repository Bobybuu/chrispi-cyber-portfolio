# fix_migrations.py
import os
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamngeny_backend.settings')
django.setup()

def fix_migrations():
    """Create migrations for all apps without URL checks"""
    
    # Temporarily disable URL checking
    from django.core.checks.registry import registry
    registry.ready = False
    
    apps = ['accounts', 'content', 'contact', 'utils', 'blog', 'portfolio', 'files']
    
    for app in apps:
        try:
            print(f"Creating migrations for {app}...")
            execute_from_command_line(['manage.py', 'makemigrations', app])
            print(f"✓ {app} migrations created")
        except Exception as e:
            print(f"✗ {app} failed: {e}")
    
    print("Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ All migrations applied")

if __name__ == "__main__":
    fix_migrations()