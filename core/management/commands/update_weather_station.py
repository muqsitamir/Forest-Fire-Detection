from datetime import timedelta

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
            print(start_ts)
            endTs_datetime = event.created_at + timedelta(minutes=10)
            endTs = int(endTs_datetime.timestamp()) * 1000
            print(endTs)
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
                ts_params = f"&startTs={start_ts}&endTs={endTs}"
                url = f"{base_url}{device_id}/values/timeseries?keys={keys}{ts_params}"
                headers = {
                    "Content-Type": "application/json",
                    "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJtdWhhbW1hZF93YXFhckBsdW1zLmVkdS5wayIsInVzZXJJZCI6ImNmMTgzMTYwLWYzNzAtMTFlZS05Mzc4LTIxNTVjZjA1NzBmOCIsInNjb3BlcyI6WyJDVVNUT01FUl9VU0VSIl0sInNlc3Npb25JZCI6ImYxNzA0NTJkLThlMTYtNDgwZC1hOWU4LTI4NzgyZGY5YmJiMiIsImlzcyI6InRoaW5nc2JvYXJkLmlvIiwiaWF0IjoxNzM0Mjk0NjQ2LCJleHAiOjE3NDIwNzA2NDYsImZpcnN0TmFtZSI6Ik11aGFtbWFkIiwibGFzdE5hbWUiOiJXYXFhciIsImVuYWJsZWQiOnRydWUsImlzUHVibGljIjpmYWxzZSwidGVuYW50SWQiOiI2YWFmMzZlMC0yZDUyLTExZWUtODM0OC0yMzc4NjQ5MWJkY2IiLCJjdXN0b21lcklkIjoiMjE1YTU1ZjAtODIzNS0xMWVlLWI2ZWEtOWQ2MDkwMzkwZjFiIn0._7a63CodyjvcMzqsZquypEw6r4iLSbr1AYASqc2Ouk_EqziCOQqw8fcrR1U69jLjsEw2Q8qNECT2_OAYIW-2Eg"}
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        weather_data = response.json()
                        air_temp_value = weather_data.get("Air_Temperature", [{}])[0].get("value")
                        air_humidity_value = weather_data.get("Air_Humidity", [{}])[0].get("value")
                        print("event")
                        print(air_humidity_value)
                        print(air_temp_value)

                        if air_temp_value is not None and air_humidity_value is not None:

                            Event.objects.filter(pk=event.pk).update(weather_station={
                                "Air_Temp": air_temp_value,
                                "Air_Humidity": air_humidity_value,
                            })

                except requests.RequestException as e:
                    print(f"Error fetching weather data for event {event.uuid}: {e}")