import logging

from django.core.management.base import BaseCommand
from core.models import Event
from glob import glob
import os


class Command(BaseCommand):
    help = 'Dangling files cleanup'

    def add_arguments(self, parser):
        # Positional arguments are standalone name
        parser.add_argument(
            '--thumbnail',
            action='store_true',
            dest='thumbnail',
            default=False,
            help='Operate on thumbnails folder',
        )

        parser.add_argument(
            '--print_unused',
            action='store_true',
            dest='print_unused',
            default=False,
            help='print unused files',
        )

        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete the files',
        )

    def handle(self, *args, **options):
        unused_files = self.unused_files(thumbnail=options['thumbnail'], prnt=options['print_unused'])
        if options['delete']:
            self.clean_files(unused_files)

    def unused_files(self, thumbnail=False, prnt=False):
        thumb_params = ('thumbnails', 'thumbnail', {'thumbnail': ''})
        folder, field, filters = thumb_params if thumbnail else ('events', 'file', {'file': ''})
        event_files = set([f'media/{file}'for file in Event.objects.exclude(**filters).values_list(field, flat=True)])
        print(f'Total Events: {Event.objects.count()}')

        print(f'Event Files: {len(event_files)}')
        total_files = set(glob(f'media/{folder}/*'))
        print(f'Total Files: {len(total_files)}')

        unused_files_set = total_files - event_files
        if prnt:
            print(unused_files_set)
        print(f'Un-used Files: {len(unused_files_set)}')
        return unused_files_set

    def clean_files(self, unused_files):
        for file in unused_files:
            try:
                os.remove(file)
            except OSError as e:
                logging.log(logging.WARNING, f"Couldn't delete file: {file}")


