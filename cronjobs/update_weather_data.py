from django_cron import CronJobBase, Schedule

from core.models import Event


class UpdateWeatherDataCronJob(CronJobBase):
    RUN_EVERY_MINS = 1536

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'update_weather_data_cron_job'

    def do(self):
        events = Event.objects.filter(weather_data__isnull=True).order_by('-created_at')[:800]

        for event in events:
            if event.created_at:
                weather_data = event.get_weather_data()
                if weather_data:
                    event.weather_data = weather_data
                    event.save()
