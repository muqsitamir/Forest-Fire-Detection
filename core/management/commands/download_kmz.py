import os
import requests
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Downloads KMZ file from NASA API'

    def handle(self, *args, **kwargs):
        firms_api_url = 'https://firms.modaps.eosdis.nasa.gov/api/kml_fire_footprints/south_asia/24h/c6.1/FirespotArea_south_asia_c6.1_24h.kmz'

        current_date = datetime.now().strftime('%Y%m%d')
        output_filename = f'{current_date}.kmz'

        # Specify the folder path in MEDIA_ROOT
        folder_path = os.path.join(settings.MEDIA_ROOT, 'kmz')

        # Check if the folder exists, create it if it doesn't
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Specify the absolute path where you want to save the KMZ file
        output_path = os.path.join(folder_path, output_filename)

        try:
            response = requests.get(firms_api_url)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            with open(output_path, 'wb') as kmz_file:
                kmz_file.write(response.content)
            self.stdout.write(self.style.SUCCESS(f'KMZ file downloaded successfully at: {output_path}'))
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Failed to download KMZ file. Error: {e}'))
