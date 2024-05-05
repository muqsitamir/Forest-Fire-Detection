import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

from core.models import Event


class Command(BaseCommand):
    help = 'Delete all false events before a certain date for a certain camera'

    def add_arguments(self, parser):
        parser.add_argument(
            'camera_id',
            help='required, will return all false events for this camera'
        )

        parser.add_argument(
            'date',
            help='Required, ; all events before this date will be deleted'
        )

        parser.add_argument(
            'month',
            help='Required; month of date'
        )

        parser.add_argument(
            'year',
            help='Required; year of date'
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
                camera__id=options['camera_id'], date__lte=datetime.date(int(options['year']), int(options['month']), int(options['date']))).exclude(Q(species="fire") | Q(species="smoke"))
        count = events.count()
        if options['delete']:
            events.delete()
            message = f"Deleted {count}"
        print(f'{message} false events before {options["date"]} - {options["month"]} - {options["year"]} for camera_id {options["camera_id"]}')