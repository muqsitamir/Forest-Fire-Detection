from django.core.management.base import BaseCommand

from core.models import Event


class Command(BaseCommand):
    help = 'Sets the weather data for remaining events in a recent first manner'

    def handle(self, *args, **options):
        events = Event.objects.filter(weather_data__isnull=True).order_by('-created_at')[:800]

        for event in events:
            try:
                weather_data = event.get_weather_data()
                if weather_data:
                    event.weather_data = weather_data
                    event.save()
            except Exception as e:
                continue
