from django.core.management.base import BaseCommand

from core.models import Event


class Command(BaseCommand):
    help = 'Sets the weather data for remaining events in a recent first manner'

    def handle(self, *args, **options):
        events = Event.objects.exclude(camera__in=[5, 6]).filter(weather_data__isnull=True).order_by('-created_at')[:50]

        for event in events:
            print(event)
            try:
                event.save()
            except Exception as e:
                print(e)
