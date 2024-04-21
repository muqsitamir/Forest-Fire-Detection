
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event
import requests

class Command(BaseCommand):
    help = 'Updates existing Event weather_station data'

    def handle(self, *args, **options):

        events = Event.objects.filter(weather_station__isnull=True)
        print("weather station")
        for event in events:
            start_ts = int(event.created_at.timestamp()) * 1000

            device_id = ""
            base_url = "http://icarus.lums.edu.pk/api/plugins/telemetry/DEVICE/"


            if event.camera_id == 5:
                device_id = "c721d8c0-3a21-11ee-9dc2-07b8268a3068"
            elif event.camera_id == 3:
                device_id = "8a86c4b0-3cb1-11ee-9dc2-07b8268a3068"
            elif event.camera_id == 6:
                device_id = "9c4c6f10-30db-11ee-9dc2-07b8268a3068"
            elif event.camera_id == 7:
                device_id = "9e6f1ab0-3a20-11ee-9dc2-07b8268a3068"

            if device_id:
                keys = "temperature,humidity,Air_Temperature,Air_Humidity,timestamp"
                ts_params = f"&startTs={start_ts}"
                url = f"{base_url}{device_id}/values/timeseries?keys={keys}{ts_params}"
                headers = {
                    "Content-Type": "application/json",
                    "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJtdWhhbW1hZF93YXFhckBsdW1zLmVkdS5wayIsInVzZXJJZCI6ImNmMTgzMTYwLWYzNzAtMTFlZS05Mzc4LTIxNTVjZjA1NzBmOCIsInNjb3BlcyI6WyJDVVNUT01FUl9VU0VSIl0sInNlc3Npb25JZCI6ImQ4ZDVjN2Q3LTUwODEtNGNjZS05ZGJjLWNmMTZmMzMwZDg2MiIsImlzcyI6InRoaW5nc2JvYXJkLmlvIiwiaWF0IjoxNzEzMzc2Nzc4LCJleHAiOjE3MTM5ODE0NzgsImZpcnN0TmFtZSI6Ik11aGFtbWFkIiwibGFzdE5hbWUiOiJXYXFhciIsImVuYWJsZWQiOnRydWUsImlzUHVibGljIjpmYWxzZSwidGVuYW50SWQiOiI2YWFmMzZlMC0yZDUyLTExZWUtODM0OC0yMzc4NjQ5MWJkY2IiLCJjdXN0b21lcklkIjoiMjE1YTU1ZjAtODIzNS0xMWVlLWI2ZWEtOWQ2MDkwMzkwZjFiIn0.vRDFHjldIC_LrRvIsoR3EscyqemKZW7pmWHaKLMi2ZYSWNZ4wDBunt_e9pDw96qKwuCyHXxH8GH3MMxkR_VG9Q"
                       }

                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        weather_data = response.json()

                        # Extract single values for Air_Temp and Air_Humidity
                        air_temp_value = weather_data.get("Air_Temperature", [{}])[0].get("value")
                        air_humidity_value = weather_data.get("Air_Humidity", [{}])[0].get("value")
                        print("event")
                        # Save the extracted values directly to weather_station
                        Event.objects.filter(pk=event.pk).update(weather_station={
                            "Air_Temp": air_temp_value,
                            "Air_Humidity": air_humidity_value,
                        })

                except requests.RequestException as e:
                    print(f"Error fetching weather data for event {event.uuid}: {e}")