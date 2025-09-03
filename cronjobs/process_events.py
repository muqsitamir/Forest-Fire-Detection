import json
import os
import cv2
import imageio
import requests
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.core.files import File
from django_cron import CronJobBase, Schedule
from core.models import Image, BoundingBox, Event, Log
import logging

# Configure logging
logger = logging.getLogger(__name__)


def email_sender(event, **kwargs):
    if event.species.filter(endangered=True).exists() and not event.sms_sent:
        send_mail(
            'Animal Detected',
            f"Camera Node ({event.camera.description}) detected {', '.join(event.species.values_list('name', flat=True))}\nGo to the following link to see the generated event\n https://api.tpilums.org.pk{event.file.url}",
            settings.EMAIL_HOST_USER,
            ['islammuqsit7@gmail.com', 'murtazataj@gmail.com', 'muzammal0@gmail.com',
             'zainulhassan540@gmail.com'],
            fail_silently=False,
        )
        event.sms_sent = True

def send_sms(event):
    contact_numbers = {x.strip(): False for x in
                       event.camera.contacts.split(",")} if not event.sms_sent_multiple else json.loads(
        event.sms_sent_multiple)
    for contact_number, sent in contact_numbers.items():
        if not sent:
            text = f"{event.camera.description} detected {', '.join(event.species.values_list('name', flat=True))}" \
                   f": https://api.forestwatch.org.pk{event.file.url}"

            for i in range(2):
                resp = requests.get(f'http://203.135.63.37:8004/', headers={'Content-Type': 'application/json'},
                                    params={"number": contact_number, "text": text}, timeout=25)
                if resp.status_code == 200:
                    contact_numbers[contact_number] = True
                    logger.info(f"Successfully sent notification to {contact_number}")
                    break

    event.sms_sent_multiple = json.dumps(contact_numbers)
    event.save()
    if any(contact_numbers.values()):
        return True
    else:
        return False

def sms_sender(event, **kwargs):
    if event.species.filter(endangered=True).exists() and not event.sms_sent:
        if event.camera.contacts and send_sms(event):
            event.sms_sent = True
            event.save()


class ProcessEventsCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'process_event_cron_job'

    def do(self):
        events = Image.objects.filter(included=False, processed=True).values_list('event_id', flat=True).distinct()

        for event in Event.objects.filter(uuid__in=events):
            event.species.clear()
            event.file.delete()
            event.thumbnail.delete()

            images_qs = Image.objects.filter(event=event, processed=True)

            with imageio.get_writer(f'{settings.MEDIA_ROOT}/temp/{event.uuid}_thumb.gif', mode='I',
                                    duration=0.5) as thumb_writer:
                with imageio.get_writer(f'{settings.MEDIA_ROOT}/temp/{event.uuid}.gif', mode='I',
                                        duration=0.5) as writer:
                    images = images_qs.order_by('file')
                    for image in images:
                        try:
                            image_data = imageio.imread(image.file.path)
                        except FileNotFoundError as e:
                            Log(message=f"Couldnt find processed image to include to event gif. FileNotFound: {image.file.path}, Marking image as included", camera=image.camera,
                                logged_at=timezone.now(), script=Log.OTHERS, activity=Log.CAMERA_ERROR).save()
                            images_qs.update(included=True)
                            continue
                        for box in BoundingBox.objects.filter(image=image):
                            # height, width = image_data.shape[:2]
                            x, y, x2, y2 = int(box.x), int(box.y), int(box.width), int(
                                box.height)
                            image_data = cv2.rectangle(image_data, (x, y), (x2, y2), (0, 0, 255), 2)
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
            event.save()
            images_qs.update(included=True)
            sms_sender(event)
