
import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yourtourguide.settings')
django.setup()

from accounts.models import TourSupplier
from accounts.admin_panel.forms import TourSupplierForm

try:
    print("Checking TourSupplier model...")
    field_names = [f.name for f in TourSupplier._meta.get_fields()]
    if 'password' in field_names:
        print("PASS: 'password' field found in TourSupplier model.")
    else:
        print("FAIL: 'password' field NOT found in TourSupplier model.")

    print("\nChecking TourSupplierForm...")
    form = TourSupplierForm()
    if 'password' in form.fields:
        print("PASS: 'password' field found in TourSupplierForm.")
        widget = form.fields['password'].widget
        from django.forms.widgets import PasswordInput
        if isinstance(widget, PasswordInput):
             print(f"PASS: Widget is PasswordInput.")
        else:
             print(f"FAIL: Widget is {type(widget)}, expected PasswordInput.")
    else:
        print("FAIL: 'password' field NOT found in TourSupplierForm.")
        print(f"Available fields: {list(form.fields.keys())}")

except Exception as e:
    print(f"ERROR: {e}")
