from rest_framework import serializers

from accounts.models import Organization
from core.models import BoundingBox, Image, Specie, Camera, Slot, Reading, Log, Event, Tower, Sensor, PTZCameraPreset, \
    EventCount, WeatherData


class SpecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specie
        fields = "__all__"


class BoxSerializer(serializers.ModelSerializer):
    specie = SpecieSerializer(read_only=True)
    image_date = serializers.DateTimeField(source='image.date', read_only=True)

    class Meta:
        model = BoundingBox
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    species = SpecieSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    camera_name = serializers.CharField(source='camera.description', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    boundingbox_set = BoxSerializer(read_only=True, many=True)
    uuid = serializers.CharField(write_only=True)

    class Meta:
        model = Image
        fields = '__all__'

    def validate(self, attrs):
        attrs['camera'] = self.context['request'].user.camera
        event, _ = Event.objects.get_or_create(uuid=attrs.pop('uuid'), defaults={'date': attrs['date'], 'camera': attrs['camera']})

        if event.date > attrs['date']:
            event.date = attrs['date']

        event.save()
        attrs['event'] = event
        return attrs


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = '__all__'


class CameraSerializer(serializers.ModelSerializer):
    slots = SlotSerializer(many=True, read_only=True)
    last_captured_at = serializers.DateTimeField(read_only=True)
    latest_event = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Camera
        fields = '__all__'

    def get_latest_event(self, obj):
        latest_event = Event.objects.filter(camera_id=obj.id).first()
        if latest_event:
            return latest_event.file.name
        return None


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'


class TowerSerializer(serializers.ModelSerializer):
    cameras = CameraSerializer(many=True, read_only=True, source='camera_set')
    sensors = SensorSerializer(many=True, read_only=True, source='sensor_set')

    class Meta:
        model = Tower
        fields = ('id', 'name', 'lat', 'lng', 'cameras', 'sensors',)


class CameraListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Camera
        fields = ('id', 'test', 'live', 'should_log', 'description', 'created_at', 'last_reported_at', 'remaining_storage')


class EventCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCount
        fields = '__all__'

class OrganizationSerializer(serializers.ModelSerializer):
    cameras = serializers.SerializerMethodField(read_only=True)
    species = SpecieSerializer(read_only=True, many=True)

    class Meta:
        model = Organization
        fields = "__all__"

    def get_cameras(self, instance):
        if self.context['request'].user.is_superuser:
            return CameraListSerializer(Camera.objects.all(), many=True).data
        qs = Camera.objects.filter(organization=instance)
        return CameraListSerializer(qs, many=True).data


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('id', 'name', 'lat', 'lng',)


class ReadingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reading
        fields = '__all__'

    def validate(self, attrs):
        attrs['camera'] = self.context['request'].user.camera
        return attrs


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = "__all__"

    def validate(self, attrs):
        attrs['camera'] = self.context['request'].user.camera
        return attrs

class PTZCameraPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTZCameraPreset
        fields = '__all__'


class WeatherDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherData
        fields = '__all__'