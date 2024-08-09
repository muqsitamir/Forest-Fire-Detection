import os
import requests
from datetime import datetime, time, timedelta
from django.conf import settings
from django_cron import CronJobBase, Schedule
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DownloadKMZCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 * 24  # Run once every 24 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Download_KMZ_Cron_Job'

    def do(self):
        desired_start_time = time(23, 50)
        current_datetime = datetime.now()

        time_until_start = datetime.combine(current_datetime.date(), desired_start_time) - current_datetime

        if time_until_start.total_seconds() < 0:
            time_until_start += timedelta(days=1)

        # Wait until the desired start time
        if time_until_start.total_seconds() > 0:
            logger.info(f"Waiting for {time_until_start.total_seconds()} seconds until the desired start time.")
            return  # Exit the method to wait until the next run

        firms_api_url = 'https://firms.modaps.eosdis.nasa.gov/api/kml_fire_footprints/south_asia/24h/c6.1/FirespotArea_south_asia_c6.1_24h.kmz'

        current_date = datetime.now().strftime('%Y%m%d')
        output_filename = f'{current_date}.kmz'
        folder_path = os.path.join(settings.MEDIA_ROOT, 'kmz')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        output_path = os.path.join(folder_path, output_filename)

        response = requests.get(firms_api_url)
        if response.status_code == 200:
            with open(output_path, 'wb') as kmz_file:
                kmz_file.write(response.content)
            logger.info(f'KMZ file downloaded successfully at: {output_path}')
        else:
            logger.error(f'Failed to download KMZ file. Status code: {response.status_code}')
