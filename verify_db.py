import os
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yourtourguide.settings')
django.setup()

from accounts.models import (
    Tour, TourPricing, TourImage, TourHighlight, TourItinerary,
    TourIncluded, TourExcluded, TourRequirement, TourFAQ, 
    TourSchedule, TourBlackoutDate
)

def check_table(model, table_name):
    model_fields = {f.column for f in model._meta.fields}
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    db_fields = {col[1] for col in cursor.fetchall()}
    conn.close()
    missing_in_db = model_fields - db_fields
    missing_in_model = db_fields - model_fields
    print(f"{model.__name__}: Model={len(model_fields)} DB={len(db_fields)}")
    if missing_in_db: print(f"  Missing DB: {list(missing_in_db)}")
    if missing_in_model - {'id'}: print(f"  Extra DB: {list(missing_in_model - {'id'})}")

check_table(TourSchedule, 'accounts_tourschedule')
check_table(TourBlackoutDate, 'accounts_tourblackoutdate')
