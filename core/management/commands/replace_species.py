from django.core.management.base import BaseCommand

from core.models import BoundingBox, Specie


class Command(BaseCommand):
    help = 'Replaces all the bounding boxes species to Animals or Persons.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        animal = Specie.objects.get(id='animal')
        for bbox in BoundingBox.objects.all():
            if bbox.specie_id not in ['person', 'vehicle']:
                bbox.specie = animal
            bbox.save()
