from django_cron import CronJobBase, Schedule
from suntime import Sun

from core.models import Camera


class SetSunTimesCronJob(CronJobBase):
    RUN_EVERY_MINS = 7200
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'set_sun_times_cron_job'

    def do(self):
        for cam in Camera.objects.all():
            lat, long = cam.latitude, cam.longitude
            sun = Sun(lat, long)
            cam.sunrise = sun.get_sunrise_time()
            cam.sunset = sun.get_sunset_time()
            cam.save()
