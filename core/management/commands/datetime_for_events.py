from datetime import timedelta, timezone

from django.core.management.base import BaseCommand

from core.models import Event


class Command(BaseCommand):
    help = 'Returns a list of Datetime objects from a QuerySet of Event Objects'

    def handle(self, *args, **options):
        events = []
        TZObject = timezone(timedelta(hours=5), name="PKST")

        for event in Event.objects.all():
            if event.image_set.count():
                event.date = event.image_set.order_by('date').first().date.astimezone(tz=TZObject)
                events.append(event)

        Event.objects.bulk_update(events, ['date'], batch_size=5000)
