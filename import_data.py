import os
import django
import csv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki_lympics.settings')
django.setup()

from athletes.models import Athletes

csv_file_path = 'INITIAL DATASET B12.csv'

with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        if not row.get('Name') or not row.get('Origin') or not row.get('Discipline'):
            continue

        name = row['Name']

        # Cek duplikasi
        if Athletes.objects.filter(athlete_name=name).exists():
            print(f"Skipped (already exists): {name}")
            continue

        athlete = Athletes(
            athlete_name=name,
            country=row['Origin'],
            sport=row['Discipline'],
            biography=row.get('Biography', 'No biography'),
            athlete_photo=row.get('Photo Profile', '')
        )
        athlete.save()
        print(f"Added: {name}")

print("DONE! All data imported, tanpa duplikat.")