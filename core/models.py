from datetime import datetime
from signal import *

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice

from core import fields
from core.storage import OverwriteStorage
import requests
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

    def get_weather_data(self):
        if self.date and self.camera:

            api_key = '13e8f6a07b4654d035d3cb3280725fe7'
            created_at=self.created_at
            longitude = self.camera.longitude
            latitude = self.camera.latitude


            unix_timestamp = int(created_at.timestamp())

            url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={unix_timestamp}&appid={api_key}'

            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()
                return weather_data
            else:
                return None
        else:
            return None


    class Meta:
        ordering = ('-created_at',)

    def captured_at(self):
        return Image.objects.filter(event=self).order_by('date')[0].date

    def __str__(self):
        return str(self.uuid)

    def save(self, *args, **kwargs):
        self.weather_data = self.get_weather_data()
        super().save(*args, **kwargs)

    def get_weather_data(self):
        if self.date and self.camera:
            api_key = 'e39776ce233e18ced07d61cbc6dbe2a1'
            date = self.date
            longitude = self.camera.longitude
            latitude = self.camera.latitude

            unix_timestamp = int(date.timestamp())

            url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={unix_timestamp}&appid={api_key}'

            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()
                return weather_data
            else:
                return None
        else:
            return None


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
