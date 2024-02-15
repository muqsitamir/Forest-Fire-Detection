from django_cron import CronJobBase, Schedule
import subprocess
from django.core.mail import send_mail

from backend import settings


class CheckDiskSpaceCronJob(CronJobBase):
    RUN_EVERY_MINS = 60
    available_space = None
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'check_disk_space_cron_job'

    def __init__(self):
        super().__init__()
        self.threshold = None

    def do(self):
        self.threshold = 5
        process = subprocess.Popen(['df'], stdout=subprocess.PIPE)
        out, err = process.communicate()
        df_output = out.decode('utf-8').split('\n')[3].split(" ")
        df_output = [item for item in df_output if item != '' and '%' not in item][3]
        self.available_space = int(df_output) / (1024 * 1024)
        if self.available_space < self.threshold:
            send_mail(
                'Camera Trap Space',
                f'Disk space is running low, remaining space: {self.available_space} \n'
                f'Remove false events from the server to free space',
                settings.EMAIL_HOST_USER,
                ['islammuqsit7@gmail.com', 'murtazataj@gmail.com', 'muzammal0@gmail.com', 'zainulhassan540@gmail.com'],
                fail_silently=False,
            )

