import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki_lympics.settings')
django.setup()

from athletes.models import Athletes
import uuid

# Baca Excel
df = pd.read_excel('INITIAL DATASET B12.xlsx')

for index, row in df.iterrows():
    # Skip jika data kosong
    if pd.isna(row['Name']) or pd.isna(row['Origin']) or pd.isna(row['Discipline']):
        continue
    
    # Buat athlete
    athlete = Athletes(
        athlete_name=row['Name'],
        country=row['Origin'],
        sport=row['Discipline'],
        biography=row.get('Biography', 'No biography'),
        athlete_photo=row.get('Photo Profile', '')
    )
    athlete.save()
    print(f"Added: {row['Name']}")

print("DONE! All data imported.")