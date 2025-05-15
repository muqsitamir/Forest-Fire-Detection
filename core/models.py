from datetime import datetime
import time
from signal import *
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from core import fields
from core.storage import OverwriteStorage
import requests
from django.utils import timezone

User = get_user_model()


class Tower(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return 'T' + str(self.id) + ' - ' + str(self.name)


class Sensor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    things_board_link = models.CharField(max_length=300, null=True, blank=True)
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=30, choices=(
        ('Temperature', 'Temperature'),
        ('Humidity', 'Humidity'),
    ), default='Temperature')

    def __str__(self):
        return 'S' + str(self.id) + ' - ' + self.sensor_type + ' - ' + str(self.tower.name)


class Camera(models.Model):
    # When True: only superuser can see the event associated with this camera on dashboard.

    test = models.BooleanField(default=True)
    # When True: Camera starts caputing events
    live = models.BooleanField(default=True)
    # When True: Camera sends logs to Django Server
    # Todo: Remove this logging.
    should_log = models.BooleanField(default=True)
    # when True: Camera doesn't switch 4g off after usage (check 4g_idol_interval)

    # Display names for camera on the event images and dashboard. # Todo: rename to "Name"
    description = models.CharField(max_length=100, blank=True)

    user = models.OneToOneField(User, on_delete=models.PROTECT, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    roi_mask = models.ImageField(null=True, blank=True, upload_to="roi_masks")
    last_reported_at = models.DateTimeField(null=True, blank=True)
    last_uploaded_at = models.DateTimeField(null=True, blank=True)
    # last_captured_at = models.DateTimeField(null=True, blank=True)
    # action = models.CharField(max_length=20, choices=ACTIONS, null=True, blank=True)
    remaining_storage = models.FloatField(default=64)
    organization = models.ForeignKey('accounts.Organization', null=True, on_delete=models.CASCADE)

    # Capture setting
    frames_per_sec = models.IntegerField(default=1)
    image_width = models.IntegerField(default=640)
    image_height = models.IntegerField(default=480)

    # thresholds
    day_threshold = models.FloatField(default=1000)
    night_threshold = models.FloatField(default=1000)
    iou_threshold = models.FloatField(default=80)

    # site
    longitude = models.FloatField(blank=True)
    latitude = models.FloatField(blank=True)
    sunset = models.DateTimeField(null=True, blank=True)
    sunrise = models.DateTimeField(null=True, blank=True)
    contact_no = models.CharField(max_length=16, null=True, blank=True)

    # pins
    infrared = models.IntegerField(default=12)
    pwm = models.IntegerField(default=100)
    filter_a = models.IntegerField(default=16)
    filter_b = models.IntegerField(default=18)
    motion_1 = models.IntegerField(default=11)
    motion_2 = models.IntegerField(default=13)
    pin_4g = models.IntegerField(default=36)

    # intervals
    rest_interval = models.IntegerField(default=5)
    motion_interval = models.IntegerField(default=2)
    video_interval = models.IntegerField(default=15)
    update_after = models.FloatField(default=300)
    idol_4g_interval = models.FloatField(default=300)

    # vercel changes
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE, null=True)
    live_image = fields.CustomImageField(storage=OverwriteStorage(), upload_to='liveimages', unique=True, null=True,
                                         blank=True)
    live_stream_url = models.CharField(max_length=100, blank=True)
    # yolo parameters
    confidence_threshold = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.2)

    def __str__(self):
        return f"ID: {self.id} ({self.description})"

    @property
    def slots(self):
        return self.slot_set.all()

    @property
    def dont_care(self):
        return self.dontcare_set.all()

    @property
    def last_captured_at(self):
        last_event = self.event_set.first()
        if last_event:
            return last_event.date


class DontCare(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)


class Slot(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    power_on_at = models.TimeField()
    power_off_at = models.TimeField()


class Image(models.Model):
    file = fields.CustomImageField(storage=OverwriteStorage(), upload_to='wwf/%Y-%m-%d', unique=True)
    camera = models.ForeignKey(Camera, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField()
    event = models.ForeignKey('Event', blank=True, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)
    included = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def get_upload_to(self, attname):
        return f'wwf/{self.camera.user.username}/{self.date.strftime("%Y-%m-%d")}'

    def __str__(self):
        return str(self.file)


class Reading(models.Model):
    ON = 'ON'
    OFF = 'OFF'

    STATUS = [
        (ON, 'On'),
        (OFF, 'Off'),
    ]

    temperature = models.FloatField(default=0)
    voltage = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, null=True, blank=True)
    camera = models.ForeignKey(Camera, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Camera {self.camera.description} ({self.temperature}|{self.voltage})"


class Specie(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    endangered = models.BooleanField(default=False)
    color = models.CharField(max_length=50, default='rgb(75, 192, 192)')
    created_at = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.id


class BoundingBox(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, )
    specie = models.ForeignKey(Specie, null=True, on_delete=models.SET_NULL)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.specie}: {self.image.id} | {self.image.file}'


class EventCount(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    total_event_count = models.IntegerField(default=0)
    total_night_event_count = models.IntegerField(default=0)
    total_day_event_count = models.IntegerField(default=0)
    fire_day_event_count = models.IntegerField(default=0)
    smoke_night_event_count = models.IntegerField(default=0)
    fire_night_event_count = models.IntegerField(default=0)
    smoke_day_event_count = models.IntegerField(default=0)
    night_event_with_more_than_one_species = models.IntegerField(default=0)
    day_event_with_more_than_one_species = models.IntegerField(default=0)

    def __str__(self):
        return f"EventCount for Camera {self.camera.id}"


class Event(models.Model):
    FEATURED = "FEATURED"
    ARCHIVED = "ARCHIVED"
    NONE = "NONE"
    STATUS = [
        (FEATURED, 'Featured'),
        (ARCHIVED, 'Archived'),
        (NONE, 'None'),
    ]

    uuid = models.UUIDField(primary_key=True)
    file = models.ImageField(storage=OverwriteStorage(), upload_to='events')
    thumbnail = models.ImageField(storage=OverwriteStorage(), upload_to='thumbnails')
    species = models.ManyToManyField(Specie, blank=True)
    date = models.DateTimeField(null=True)
    camera = models.ForeignKey(Camera, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sms_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default=NONE)
    weather_data = models.JSONField(null=True, blank=True)
    nasa_tag = models.BooleanField(default=False)
    weather_station = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def captured_at(self):
        return Image.objects.filter(event=self).order_by('date')[0].date

    def __str__(self):
        return str(self.uuid)

    def day(self):
        return self.created_at.date()

    def save(self, *args, **kwargs):

        if self.weather_data is None:
            rate_limit_result = self.check_weather_api_rate_limit()
            if rate_limit_result != "OK":
                raise SuspiciousOperation(rate_limit_result)

            self.weather_data = self.get_weather_data()
        if self.weather_station is None:
            self.weather_station = self.check_weather_station_api()
        self.update_event_counts()
        super().save(*args, **kwargs)

    def update_event_counts(self):
        event_count, created = EventCount.objects.get_or_create(camera=self.camera)
        try:
            event = Event.objects.filter(camera=self.camera).first()
            total_event_count = event_count.total_event_count
            total_night_event_count = event_count.total_night_event_count
            total_day_event_count = event_count.total_day_event_count
            fire_day_event_count = event_count.fire_day_event_count
            smoke_night_event_count = event_count.smoke_night_event_count
            fire_night_event_count = event_count.fire_night_event_count
            smoke_day_event_count = event_count.smoke_day_event_count
            night_event_with_more_than_one_species = event_count.night_event_with_more_than_one_species
            day_event_with_more_than_one_species = event_count.day_event_with_more_than_one_species
            if event:
                created_at = event.created_at
                print(created_at)
                is_night = created_at.time().hour >= 18 or created_at.time().hour <= 6
                # Retrieve all related species objects
                species_list = event.species.all()
                print(species_list.count())
                for species in species_list:
                    print(species.id)
                has_more_than_one_species = species_list.count() > 1

                if is_night:
                    total_night_event_count += 1
                    if has_more_than_one_species:
                        night_event_with_more_than_one_species += 1

                    # Check each species in the event
                    for species in species_list:
                        print(species.id)
                        if species.id == 'fire':
                            fire_night_event_count += 1
                        if species.id == 'smoke':
                            smoke_night_event_count += 1
                else:
                    total_day_event_count += 1
                    if has_more_than_one_species:
                        day_event_with_more_than_one_species += 1

                    # Check each species in the event
                    for species in species_list:
                        if species.id == 'fire':
                            fire_day_event_count += 1
                        if species.id == 'smoke':
                            smoke_day_event_count += 1
            else:
                pass
        except Event.DoesNotExist:
            raise ValueError("Event with the specified UUID does not exist")
        total_event_count += 1
        event_count.total_event_count = total_event_count
        event_count.total_night_event_count = total_night_event_count
        event_count.total_day_event_count = total_day_event_count
        event_count.fire_day_event_count = fire_day_event_count
        event_count.smoke_night_event_count = smoke_night_event_count
        event_count.fire_night_event_count = fire_night_event_count
        event_count.smoke_day_event_count = smoke_day_event_count
        event_count.night_event_with_more_than_one_species = night_event_with_more_than_one_species
        event_count.day_event_with_more_than_one_species = day_event_with_more_than_one_species

        print("Total night events:", total_night_event_count)
        print("Night events with more than one species:", night_event_with_more_than_one_species)
        print("Fire night events:", fire_night_event_count)
        print("Smoke night events:", smoke_night_event_count)

        print("Total day events:", total_day_event_count)
        print("Day events with more than one species:", day_event_with_more_than_one_species)
        print("Fire day events:", fire_day_event_count)
        print("Smoke day events:", smoke_day_event_count)

        event_count.save()

    def check_weather_station_api(self):
        current_time = timezone.now()
        print(self.created_at)
        start_ts = int(current_time.timestamp()) * 1000
        device_id = ""
        base_url = "http://icarus.lums.edu.pk/api/plugins/telemetry/DEVICE/"
        print(self.camera_id)
        if self.camera_id == 5:
            device_id = "c721d8c0-3a21-11ee-9dc2-07b8268a3068"
        elif self.camera_id == 3:
            device_id = "8a86c4b0-3cb1-11ee-9dc2-07b8268a3068"
        elif self.camera_id == 6:
            device_id = "9c4c6f10-30db-11ee-9dc2-07b8268a3068"
        elif self.camera_id == 7:
            device_id = "9e6f1ab0-3a20-11ee-9dc2-07b8268a3068"
        if device_id:
            keys = "Air_Temperature,Air_Humidity"
            ts_params = f"&startTs={start_ts}"
            url = f"{base_url}{device_id}/values/timeseries?keys={keys}{ts_params}"
            headers = {
                "Content-Type": "application/json",
                "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJtdWhhbW1hZF93YXFhckBsdW1zLmVkdS5wayIsInVzZXJJZCI6ImNmMTgzMTYwLWYzNzAtMTFlZS05Mzc4LTIxNTVjZjA1NzBmOCIsInNjb3BlcyI6WyJDVVNUT01FUl9VU0VSIl0sInNlc3Npb25JZCI6ImYxNzA0NTJkLThlMTYtNDgwZC1hOWU4LTI4NzgyZGY5YmJiMiIsImlzcyI6InRoaW5nc2JvYXJkLmlvIiwiaWF0IjoxNzM0Mjk0NjQ2LCJleHAiOjE3NDIwNzA2NDYsImZpcnN0TmFtZSI6Ik11aGFtbWFkIiwibGFzdE5hbWUiOiJXYXFhciIsImVuYWJsZWQiOnRydWUsImlzUHVibGljIjpmYWxzZSwidGVuYW50SWQiOiI2YWFmMzZlMC0yZDUyLTExZWUtODM0OC0yMzc4NjQ5MWJkY2IiLCJjdXN0b21lcklkIjoiMjE1YTU1ZjAtODIzNS0xMWVlLWI2ZWEtOWQ2MDkwMzkwZjFiIn0._7a63CodyjvcMzqsZquypEw6r4iLSbr1AYASqc2Ouk_EqziCOQqw8fcrR1U69jLjsEw2Q8qNECT2_OAYIW-2Eg",
            }
            print(url)
            try:
                response = requests.get(url, headers=headers)
                print(response.status_code)
                if response.status_code == 200:
                    weather_data = response.json()
                    print(weather_data)
                    if weather_data:
                        air_temp_value = weather_data.get("Air_Temperature", [{}])[0].get("value")
                        air_humidity_value = weather_data.get("Air_Humidity", [{}])[0].get("value")

                        self.weather_station = {
                            "Air_Temp": air_temp_value,
                            "Air_Humidity": air_humidity_value,
                        }

                        return self.weather_station
            except requests.RequestException as e:
                print(f"Error fetching weather data: {e}")
                return 'null'

    def check_weather_api_rate_limit(self):
        daily_key = "weather_api_daily"
        cache.add(daily_key, 0)
        print("in limit function")
        daily_count = cache.get(daily_key, 0)
        if daily_count >= 900:
            return "Daily API call limit exceeded"

        current_timestamp = int(time.time())
        minute_key = "weather_api_minute"
        cache.add(minute_key, 0)
        minute_count = cache.get(minute_key, 0, )
        if (current_timestamp - cache.get("last_api_call_timestamp", 0)) < 60 and minute_count >= 55:
            return "API call limit exceeded for this minute"

        cache.incr(daily_key)
        cache.incr(minute_key)
        cache.set("last_api_call_timestamp", current_timestamp)

        return "OK"

    def get_weather_data(self):

        if self.date and self.camera:
            api_key = 'fd4cb04cf440021f2d0fca118aa89858'
            date = self.date
            longitude = self.camera.longitude
            latitude = self.camera.latitude
            print("in get_weather_data function")
            unix_timestamp = int(date.timestamp())

            url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={unix_timestamp}&appid={api_key}'

            response = requests.get(url)
            print(response.status_code)
            if response.status_code == 200:
                weather_data = response.json()
                print(weather_data)
                return weather_data
            else:
                return "N/A"
        else:
            return "N/A"

    def update_event_counts_after_delete(sender, instance, **kwargs):
        camera_id = instance.camera.id
        EventCount.update_event_counts(camera_id)


class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    cameras = models.ManyToManyField(Camera, related_name='permissions')
    type = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View'),
            ('annotate', 'Annotate'),
            ('delete', 'Delete'),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'type'], name='unique_user_type')
        ]

    def __str__(self):
        return f"{self.user} - {self.type}"


class Log(models.Model):
    OTHERS = "OTHERS"
    SCRIPT = [
        ("CAPTURE", 'Capture'),
        ("UPLOAD", 'Upload'),
        (OTHERS, 'Others'),
    ]

    SMS_FAILED = 'SMS_FAILED'
    ALIVE = 'ALIVE'
    SCRIPT_STARTED = 'SCRIPT_STARTED'
    CAMERA_ERROR = 'CAMERA_ERROR'
    CHECKED_MOTION = 'CHECKED_MOTION'
    EVENT_CAPTURED = 'EVENT_CAPTURED'
    UPLOAD_SUCCESS = 'UPLOAD_SUCCESS'
    UPLOAD_FAILED = 'UPLOAD_FAILED'
    DETECTOR_FAULT = 'DETECTOR_FAULT'

    ACTIVITY = [
        (SMS_FAILED, 'SMS FAILED'),
        (ALIVE, 'ALIVE'),
        (SCRIPT_STARTED, 'SCRIPT STARTED'),
        (CAMERA_ERROR, 'CAMERA ERROR'),
        (CHECKED_MOTION, 'CHECKED MOTION'),
        (EVENT_CAPTURED, 'EVENT CAPTURED'),
        (UPLOAD_SUCCESS, 'UPLOAD SUCCESS'),
        (UPLOAD_FAILED, 'UPLOAD FAILED'),
        (DETECTOR_FAULT, 'DETECTOR FAULT'),
    ]

    activity = models.CharField(max_length=20, choices=ACTIVITY)
    script = models.CharField(max_length=20, choices=SCRIPT)
    message = models.CharField(max_length=200)
    logged_at = models.DateTimeField()
    camera = models.ForeignKey(Camera, blank=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


@receiver(pre_delete, sender=Event)
def event_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
    instance.thumbnail.delete(False)


@receiver(post_save, sender=Image)
def set_uploaded_at(sender, instance, **kwargs):
    instance.camera.last_uploaded_at = datetime.now()
    instance.camera.save()


class PTZCameraPreset(models.Model):
    camera_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    zoom_min = models.FloatField()
    zoom_max = models.FloatField()
    zoom_default = models.FloatField()
    pan_min = models.FloatField()
    pan_max = models.FloatField()
    pan_default = models.FloatField()
    tilt_min = models.FloatField()
    tilt_max = models.FloatField()
    tilt_default = models.FloatField()
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.camera_id} - {self.name}"


class WeatherData(models.Model):
    camera_id = models.IntegerField()
    air_temp = models.FloatField(null=True, blank=True)
    air_humidity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Camera {self.camera_id} - {self.timestamp}"
