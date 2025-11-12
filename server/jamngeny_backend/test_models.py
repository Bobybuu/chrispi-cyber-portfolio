# Create a test file test_models.py in your project root
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamngeny_backend.settings')
django.setup()

try:
    from content.models import About, Service
    from contact.models import ContactMessage, ContactSetting
    from utils.models import SystemSetting
    
    print("✓ All models imported successfully!")
    
    # Test creating instances
    about = About(
        name="Robert Jamngeny",
        title="ICT & Cybersecurity Specialist",
        bio="Test bio"
    )
    print("✓ About model works!")
    
    service = Service(
        title="Test Service",
        description="Test description"
    )
    print("✓ Service model works!")
    
    contact_setting = ContactSetting()
    print("✓ ContactSetting model works!")
    
    system_setting = SystemSetting()
    print("✓ SystemSetting model works!")
    
except Exception as e:
    print(f"✗ Error: {e}")