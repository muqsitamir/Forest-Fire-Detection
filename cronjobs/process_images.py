import json
import os

import requests
from django.conf import settings
from django.utils import timezone
from django_cron import CronJobBase, Schedule

from core.models import Image, Log, BoundingBox
from core.utils import is_dont_care


class ProcessImagesCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'process_images_cron_job'

    def do(self):
        log = False
        for image in Image.objects.filter(processed=False, included=False):
            filename = os.path.basename(image.file.name)
            files = [
                ('file', (filename, open(f'{settings.BASE_DIR}/media/{image.file.name}', 'rb'), 'image/png'))
            ]
            payload = {"camera": image.event.camera.description, "event_id": image.event.uuid}
            try:
                boxes = json.loads(requests.post(settings.MODEL_SERVICE_URL, files=files, data=payload, timeout=15).text)
                if len(boxes) > 2:
                    boxes = boxes['predictions']
                else:
                    boxes = []
            except Exception as e:
                log = True
                error_message = str(e)
                boxes = []
            index = 0
            for box in boxes:
                box_dict = {
                    'y': box['ymin'],
                    'x': box['xmin'],
                    'height': box['ymax'],
                    'width': box['xmax']
                }
                if box['class'] == 0:
                    box_dict['specie_id'] = "smoke"
                elif box['class'] == 1:
                    box_dict['specie_id'] = "fire"
                boxes[index] = box_dict
                index += 1

            boxes = [BoundingBox(image=image, **box) for box in boxes if not is_dont_care(box, image.camera)]

            BoundingBox.objects.bulk_create(boxes)
            image.processed = True
            image.save()
        if log:
            Log(message=f"Couldn't Process Frame, Error: {error_message}", camera=image.camera,
                logged_at=timezone.now(), script=Log.OTHERS, activity=Log.DETECTOR_FAULT).save()
