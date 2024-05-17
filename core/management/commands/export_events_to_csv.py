import csv
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event, Camera  # Adjust this import based on your models' location

class Command(BaseCommand):
    help = 'Export events data of the last two months for each camera to a CSV file'

    def handle(self, *args, **kwargs):
        # Calculate the date range for the last two months
        end_date = timezone.now()
        start_date = end_date - timedelta(days=60)

        # Query the events within the date range
        recent_events = Event.objects.filter(created_at__range=(start_date, end_date))

        # Get the last event for each camera if no recent events exist
        cameras = Camera.objects.all()
        camera_last_events = {}
        for camera in cameras:
            last_event = Event.objects.filter(camera=camera).order_by('-created_at').first()
            if last_event:
                camera_last_events[camera.id] = last_event

        # Prepare the CSV file
        file_name = 'events_last_two_months.csv'
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Camera ID', 'Camera Name', 'Event Created At'])

            # Write recent events to CSV
            for event in recent_events:
                camera = event.camera  # Adjust this based on your Event model's relationship with Camera
                writer.writerow([camera.id, camera.description, event.created_at])

            # Write the last event for each camera if not already included
            for camera_id, last_event in camera_last_events.items():
                if last_event.created_at < start_date:
                    camera = last_event.camera
                    writer.writerow([camera.id, camera.description, last_event.created_at])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported events to {file_name}'))
