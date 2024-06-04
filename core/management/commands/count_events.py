from django.core.management.base import BaseCommand
from core.models import Event, EventCount, Camera
from django.db.models import Count
from django.utils import timezone

class Command(BaseCommand):
    help = 'Counts all previous events for all cameras and updates EventCount model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Counting events...')

        # Clear previous counts
        EventCount.objects.all().delete()

        cameras = Camera.objects.all()
        for camera in cameras:
            events = Event.objects.filter(camera=camera)
            total_event_count = events.count()
            total_night_event_count = events.filter(created_at__hour__gte=18).count()
            total_day_event_count = events.filter(created_at__hour__lt=18).count()

            fire_night_event_count = events.filter(created_at__hour__gte=18, species__name='fire').count()
            smoke_night_event_count = events.filter(created_at__hour__gte=18, species__name='smoke').count()
            fire_day_event_count = events.filter(created_at__hour__lt=18, species__name='fire').count()
            smoke_day_event_count = events.filter(created_at__hour__lt=18, species__name='smoke').count()

            night_event_with_more_than_one_species = events.filter(created_at__hour__gte=18).annotate(num_species=Count('species')).filter(num_species__gt=1).count()
            day_event_with_more_than_one_species = events.filter(created_at__hour__lt=18).annotate(num_species=Count('species')).filter(num_species__gt=1).count()

            EventCount.objects.create(
                camera=camera,
                total_event_count=total_event_count,
                total_night_event_count=total_night_event_count,
                total_day_event_count=total_day_event_count,
                fire_night_event_count=fire_night_event_count,
                smoke_night_event_count=smoke_night_event_count,
                fire_day_event_count=fire_day_event_count,
                smoke_day_event_count=smoke_day_event_count,
                night_event_with_more_than_one_species=night_event_with_more_than_one_species,
                day_event_with_more_than_one_species=day_event_with_more_than_one_species,
            )

            self.stdout.write(f'Counted events for camera {camera.id}')

        self.stdout.write('Finished counting events')
