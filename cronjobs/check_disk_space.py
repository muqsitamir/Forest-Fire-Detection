import shutil

from django_cron import CronJobBase, Schedule
from django.core.mail import send_mail

from backend import settings


class CheckDiskSpaceCronJob(CronJobBase):
    RUN_EVERY_MINS = 200
    available_space = None
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'check_disk_space_cron_job'

    def __init__(self):
        super().__init__()
        self.threshold = 4

    def do(self):
        total, used, free = shutil.disk_usage("/")

        free_gb = free / (1024 ** 3)

        if free_gb < self.threshold:
            send_mail(
                subject='⚠️ Low Disk Space Alert - Forest Fire',
                message=(
                    f'Disk space is running low.\n\n'
                    f'Remaining free space: {free_gb:.2f} GB\n\n'
                    f'Please remove unnecessary files/logs or delete old events.'
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[
                    'islammuqsit7@gmail.com',
                    'murtazataj@gmail.com',
                    'muzammal0@gmail.com',
                ],
                fail_silently=False,
            )
