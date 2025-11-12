# clean_migrate.py
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamngeny_backend.settings')

def run_migrations():
    """Run migrations without URL checks"""
    try:
        # Setup Django
        django.setup()
        
        # Import after setup
        from django.core.management import execute_from_command_line
        
        print("Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✓ All migrations completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()