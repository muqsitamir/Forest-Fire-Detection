import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from core.models import Event


class Command(BaseCommand):
    help = 'Delete all false events before a certain date for a certain camera'

    def add_arguments(self, parser):
        parser.add_argument(
            'camera_id',
            help='required, will return all false events for this camera'
        )

        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete the selected events, if not used, the command will return the count only.',
        )

    def handle(self, *args, **options):
        events = Event.objects.filter(
                camera__id=options['camera_id']).exclude(Q(species="fire") | Q(species="smoke")).exclude(status="FEATURED")

        one_month_ago = timezone.now() - datetime.timedelta(days=30)
        events_in_latest_month = events.filter(date__gte=one_month_ago)

        if events_in_latest_month.count() > 100:
            events = events.filter(date__lte=one_month_ago)
        else:
            events_to_keep_ids = events[:100].values_list('uuid', flat=True)
            events = events.exclude(uuid__in=list(events_to_keep_ids))
        message = events.count()


        if options['delete']:
            if events:
                events.delete()
            message = f"Deleted {message}"

        print(f'{message} deletable events for camera_id {options["camera_id"]}')