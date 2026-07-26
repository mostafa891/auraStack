import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")
django.setup()

from django.core.management import call_command

print("Making migrations for payments...")
call_command("makemigrations", "payments")
print("Running migrations...")
call_command("migrate")
print("Migrations completed successfully!")
