# myapp/management/commands/update_weather_data.py

from django.core.management.base import BaseCommand
from core.models import Event  # Import your Event model

class Command(BaseCommand):
    help = 'Update weather data for existing events'

    def handle(self, *args, **kwargs):
        events = Event.objects.filter(weather_data__isnull=True)

        for event in events:
            # Fetch weather data only if the event has a valid created_at date
            if event.created_at:
                weather_data = event.get_weather_data()
                if weather_data:
                    event.weather_data = weather_data
                    event.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated weather data for Event {event.uuid}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Unable to fetch weather data for Event {event.uuid}'))
            else:
                self.stdout.write(self.style.WARNING(f'Event {event.uuid} does not have a valid created_at date'))