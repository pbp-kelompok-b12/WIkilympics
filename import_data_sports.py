import os
import django
import csv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki_lympics.settings')
django.setup()

from sports.models import Sports

csv_file_path = 'sports_dataset.csv'

with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        if not row.get('sport_name'):
            continue

        # Cek duplikasi berdasarkan sport_name
        if Sports.objects.filter(sport_name=row.get('sport_name')).exists():
            print(f"Skipped (already exists): {row.get('sport_name')}")
            continue

        sport = Sports(
            sport_name=row.get('sport_name', ''),
            sport_img=row.get('sport_img', ''),
            sport_description=row.get('sport_description', 'No description available'),
            participation_structure=row.get('participation_structure', 'individual'),
            sport_type=row.get('sport_type', 'athletic_sport'),
            country_of_origin=row.get('country_of_origin', 'Unknown'),
            country_flag_img=row.get('country_flag_img', ''),
            first_year_played=int(row.get('first_year_played', 0) or 0),
            history_description=row.get('history_description', 'No history provided'),
            equipment=row.get('equipment', 'No equipment listed')
        )
        sport.save()
        print(f"Added: {sport.sport_name}")

print("DONE! Import CSV selesai, tanpa duplikat.")