from fcm_django.models import FCMDevice


def send_push_notification(event):
    subject = f'Detected {",".join([specie.name for specie in event.species.all()])} on Camera {event.camera}!'
    devices = FCMDevice.objects.all()
    devices.send_message(title=subject, body="Message", data={"event": event.file.url})
