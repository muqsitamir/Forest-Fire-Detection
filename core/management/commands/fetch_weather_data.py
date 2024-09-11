from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Camera
from core.models import WeatherData# Assuming you have a Camera model
import requests

class Command(BaseCommand):
    help = 'Fetch weather data for all cameras'

    def handle(self, *args, **kwargs):
        current_time = timezone.now()
        start_time = current_time - timedelta(hours=34)  # 17 hours before current time
        end_time = current_time - timedelta(hours=17)
        # Convert both start_time and current_time to timestamps in milliseconds
        start_ts = int(start_time.timestamp()) * 1000
        end_ts = int(end_time.timestamp()) * 1000
        device_ids = {
            5: "c721d8c0-3a21-11ee-9dc2-07b8268a3068",
            3: "8a86c4b0-3cb1-11ee-9dc2-07b8268a3068",
            6: "9c4c6f10-30db-11ee-9dc2-07b8268a3068",
            7: "9e6f1ab0-3a20-11ee-9dc2-07b8268a3068",
        }
        base_url = "http://icarus.lums.edu.pk/api/plugins/telemetry/DEVICE/"
        keys = "Air_Temperature,Air_Humidity"
        headers = {
            "Content-Type": "application/json",
            "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJtdWhhbW1hZF93YXFhckBsdW1zLmVkdS5wayIsInVzZXJJZCI6ImNmMTgzMTYwLWYzNzAtMTFlZS05Mzc4LTIxNTVjZjA1NzBmOCIsInNjb3BlcyI6WyJDVVNUT01FUl9VU0VSIl0sInNlc3Npb25JZCI6ImYxNzA0NTJkLThlMTYtNDgwZC1hOWU4LTI4NzgyZGY5YmJiMiIsImlzcyI6InRoaW5nc2JvYXJkLmlvIiwiaWF0IjoxNzIyNDUzNDYwLCJleHAiOjE3MzAyMjk0NjAsImZpcnN0TmFtZSI6Ik11aGFtbWFkIiwibGFzdE5hbWUiOiJXYXFhciIsImVuYWJsZWQiOnRydWUsImlzUHVibGljIjpmYWxzZSwidGVuYW50SWQiOiI2YWFmMzZlMC0yZDUyLTExZWUtODM0OC0yMzc4NjQ5MWJkY2IiLCJjdXN0b21lcklkIjoiMjE1YTU1ZjAtODIzNS0xMWVlLWI2ZWEtOWQ2MDkwMzkwZjFiIn0.8cN5r-CywA3gVPjsod0cwtF-Yqv8rB4g4-ANUO-P0TzHfKbuPDdopTvMqlUavWewuYgepODlXLsD-mE_Y3Dfaw"
        }

        for camera_id, device_id in device_ids.items():
            ts_params = f"&startTs={start_ts}&endTs={end_ts}"
            url = f"{base_url}{device_id}/values/timeseries?keys={keys}{ts_params}"
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    weather_data = response.json()
                    #print(weather_data)
                    air_temp_data = []
                    air_humidity_data = []

                    # Loop through the list of Air_Temperature values with timestamps
                    for entry in weather_data.get("Air_Temperature", []):
                        # Get the 'value' and 'timestamp' fields from each entry
                        value = entry.get("value")
                        #print("temp value:"+value)
                        timestamp = entry.get("ts")
                        #print(timestamp)# Assuming the timestamp is in the entry
                        if value is not None and timestamp is not None:
                            air_temp_data.append({"value": value, "timestamp": timestamp})

                    # Loop through the list of Air_Humidity values with timestamps
                    for entry in weather_data.get("Air_Humidity", []):
                        # Get the 'value' and 'timestamp' fields from each entry

                        value = entry.get("value")
                        #print("humidity value:" + value)
                        timestamp = entry.get("ts")  # Assuming the timestamp is in the entry
                        #print(timestamp)
                        if value is not None and timestamp is not None:
                            air_humidity_data.append({"value": value, "timestamp": timestamp})

                    min_length = min(len(air_temp_data), len(air_humidity_data))
                    print(min_length)
                    #print(air_temp_data)
                    #print(air_humidity_data)
                    # Save the weather data to the database
                    for i in range(min_length):
                        #print("inside loop")
                        temp_entry = air_temp_data[i]
                        humidity_entry = air_humidity_data[i]
                        print(temp_entry['timestamp'])
                        timestamp_ms = temp_entry['timestamp']
                        timestamp_s = timestamp_ms / 1000.0

                        # Convert to datetime object
                        dt = datetime.fromtimestamp(timestamp_s)

                        # Format datetime object to a string
                        naive_dt = datetime.fromtimestamp(timestamp_s)

                        # Make datetime object timezone-aware
                        aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

                        # Format datetime object to a string
                        formatted_timestamp = aware_dt.strftime('%Y-%m-%d %H:%M:%S')  # Change format as needed

                          # Change format as needed

                        print(f'Timestamp: {formatted_timestamp}')
                        WeatherData.objects.create(
                            camera_id=camera_id,
                            air_temp=temp_entry['value'],
                            air_humidity=humidity_entry['value'],
                            timestamp=aware_dt
                        )
                    self.stdout.write(self.style.SUCCESS(f'Successfully fetched weather data for camera {camera_id}'))
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Error fetching weather data for camera {camera_id}: {e}'))
