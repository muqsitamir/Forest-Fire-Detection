from django.core.management.base import BaseCommand
from core.models import Event  # Import your Event model

class Command(BaseCommand):
    help = 'Set weather_station attribute to null for all events'

    def handle(self, *args, **kwargs):
        try:
            Event.objects.all().update(weather_station=None)
            self.stdout.write(self.style.SUCCESS('Successfully updated weather_station attribute to null for all events.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error updating weather_station attribute: {e}'))
