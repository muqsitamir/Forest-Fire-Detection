from django_cron import CronJobBase, Schedule

from core.models import Event


class UpdateWeatherDataCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'update_weather_data_cron_job'

    def do(self):
        events = Event.objects.filter(weather_data__isnull=True)

        for event in events:
            # Fetch weather data only if the event has a valid created_at date
            if event.created_at:
                weather_data = event.get_weather_data()
                if weather_data:
                    event.weather_data = weather_data
                    event.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated weather data for Event {event.uuid}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Unable to fetch weather data for Event {event.uuid}'))