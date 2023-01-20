import json

import requests
from django.conf import settings


def send_sms(event):
    text = f"Camera Node ({event.camera.description}) detected {', '.join(event.species.values_list('name', flat=True))} " \
           f". Go to the following link to see the generated event\n https://api.tpilums.org.pk{event.file.url}"
    resp = requests.post(f'{settings.MODEL_SERVICE_URL}sms/', headers={'Content-Type': 'application/json'},
                         data=json.dumps({"to": event.camera.contact_no, "text": text}))
    return True if resp.status_code == 200 else False
