import os

import cv2
import imageio
from django.conf import settings
from django.core.files import File
from django_cron import CronJobBase, Schedule

from core.models import Image, BoundingBox, Event
from core.sms_utils import send_sms


class ProcessEventsCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'process_event_cron_job'

    def do(self):
        events = Image.objects.filter(included=False).values_list('event_id', flat=True).distinct()

        for event in Event.objects.filter(uuid__in=events):
            event.species.clear()
            event.file.delete()
            event.thumbnail.delete()

            images_qs = Image.objects.filter(event=event)

            with imageio.get_writer(f'{settings.MEDIA_ROOT}/temp/{event.uuid}_thumb.gif', mode='I',
                                    duration=0.5) as thumb_writer:
                with imageio.get_writer(f'{settings.MEDIA_ROOT}/temp/{event.uuid}.gif', mode='I',
                                        duration=0.5) as writer:
                    images = images_qs.order_by('file')
                    for image in images:
                        image_data = imageio.imread(image.file.path)

                        for box in BoundingBox.objects.filter(image=image):
                            height, width = image_data.shape[:2]
                            x, y, w, h = int(box.x * width), int(box.y * height), int(box.width * width), int(
                                box.height * height)
                            image_data = cv2.rectangle(image_data, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            event.species.add(box.specie)

                        writer.append_data(image_data)
                        thumb_writer.append_data(cv2.resize(image_data, (100, 100)))

            event.date = images[0].date

            with open(f'{settings.MEDIA_ROOT}/temp/{event.uuid}.gif', 'rb') as event_gif:
                event.file.save(f'{event.uuid}.gif', File(event_gif), save=True)

            with open(f'{settings.MEDIA_ROOT}/temp/{event.uuid}_thumb.gif', 'rb') as thumb_gif:
                event.thumbnail.save(f'{event.uuid}.gif', File(thumb_gif), save=True)

            os.remove(f'{settings.MEDIA_ROOT}/temp/{event.uuid}.gif')
            os.remove(f'{settings.MEDIA_ROOT}/temp/{event.uuid}_thumb.gif')
            self.sms_sender(event)
            event.save()
            images_qs.update(included=True)

    def sms_sender(self, event, **kwargs):
        if event.species.filter(endangered=True).exists() and not event.sms_sent:
            if event.camera.contact_no and send_sms(event):
                event.sms_sent = True
