from suntime import Sun
from django.core.management.base import BaseCommand

from core.models import Camera


class Command(BaseCommand):
    help = 'Returns a list of Datetime objects from a QuerySet of Event Objects'

    def handle(self, *args, **options):
        for cam in Camera.objects.all():
            lat, long = cam.latitude, cam.longitude
            sun = Sun(lat, long)
            cam.sunrise = sun.get_sunrise_time()
            cam.sunset = sun.get_sunset_time()
            cam.save()
