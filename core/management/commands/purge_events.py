import os

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, timezone
from core.models import Image, Event


class Command(BaseCommand):
    help = 'Purges the events and their gifs given a Camera'

    def add_arguments(self, parser):
        # Positional arguments are standalone name
        parser.add_argument('camera_id')

    def handle(self, *args, **options):
        events_qs = Event.objects.filter(camera_id=options['camera_id'])
        event_files = [f'media/{gif}' for gif in events_qs.values_list('file', flat=True)]
        event_files += [f'media/{thumb}' for thumb in events_qs.values_list('thumbnail', flat=True)]
        for file in event_files:
            try:
                os.remove(file)
            except OSError:
                pass

        events_qs.delete()
