from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, timezone
from core.models import Image


class Command(BaseCommand):
    help = 'Returns a list of Datetime objects from a QuerySet of Image Objects'

    def handle(self, *args, **options):
        imgs = []
        TZObject = timezone(timedelta(hours=5), name="PKST")

        for image in Image.objects.all():
            timestamp = image.file.name[image.file.name.rfind('/')+1:-4]
            if "e" in timestamp:
                timestamp = timestamp[:timestamp.find('e') + 3]

            image.date = datetime.fromtimestamp(float(timestamp)/1000, TZObject)
            imgs.append(image)
        Image.objects.bulk_update(imgs, ['date'], batch_size=5000)
