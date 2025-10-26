import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki_lympics.settings')
django.setup()

from sports.models import Sports

# Baca Excel
df = pd.read_excel('sports_dataset.xlsx')

for index, row in df.iterrows():
    # Skip baris kosong jika tidak ada sport_name
    if pd.isna(row['sport_name']):
        continue

    # Buat instance Sports
    sport = Sports(
        sport_name=row['sport_name'],
        sport_img=row.get('sport_img', ''),
        sport_description=row.get('sport_description', 'No description available'),
        participation_structure=row.get('participation_structure', 'individual'),
        sport_type=row.get('sport_type', 'athletic_sport'),
        country_of_origin=row.get('country_of_origin', 'Unknown'),
        country_flag_img=row.get('country_flag_img', ''),
        first_year_played=int(row.get('first_year_played', 0)),
        history_description=row.get('history_description', 'No history provided'),
        equipment=row.get('equipment', 'No equipment listed')
    )

    sport.save()
    print(f"Added: {sport.sport_name}")

print("DONE! All sports data imported successfully.")