import os
from datetime import datetime, timedelta
from time import sleep
from django.utils import timezone
import json
import paho.mqtt.client as mqtt
import certifi
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
import http.client
import django_filters
import imageio
import cv2
from django.conf import settings
from django.core.files import File
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.widgets import CSVWidget
from paho import mqtt
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Organization
from core.api.serializers import ImageSerializer, BoxSerializer, CameraSerializer, \
    ReadingSerializer, LogSerializer, EventSerializer, OrganizationSerializer, TowerSerializer, \
    PTZCameraPresetSerializer, EventCountSerializer, WeatherDataSerializer
from core.models import (BoundingBox, Image, Specie, Camera, Reading, Log, Event, Tower, PTZCameraPreset, EventCount,
                         WeatherData)
from core.notifications import send_push_notification


class DynamicPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class TowerViewSet(viewsets.ModelViewSet):
    queryset = Tower.objects.all()
    serializer_class = TowerSerializer


class ImageFilterSet(filters.FilterSet):
    date_gte = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    date_lte = django_filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = Image
        fields = ['date_gte', 'date_lte']


class EventFilterSet(filters.FilterSet):
    date_gte = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    date_lte = django_filters.DateFilter(field_name="date", lookup_expr='lte')
    cameras = django_filters.ModelMultipleChoiceFilter(field_name="camera", widget=CSVWidget,
                                                       queryset=Camera.objects.all())
    species = django_filters.ModelMultipleChoiceFilter(field_name="species", widget=CSVWidget,
                                                       queryset=Specie.objects.all())
    status = django_filters.ChoiceFilter(choices=Event.STATUS)

    class Meta:
        model = Event
        fields = ['date_gte', 'date_lte', 'cameras', 'species', 'status']


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilterSet
    pagination_class = DynamicPagination

    def get_queryset(self):
        qs = self.queryset.exclude(file='')

        # Get date range from filter parameters
        if not self.request.user.is_superuser:
            # qs = qs.annotate(num_species=Count('species')).filter(num_species__gt=0, camera__test=False)
            qs = qs.filter(Q(species="vehicle") | Q(species="animal") | Q(species="person")).filter(
                camera__test=False).distinct()

        return qs.order_by('-date')

    @action(methods=['POST'], detail=False)
    def batch_update(self, request, *args, **kwargs):
        archived = request.data.get('archived', [])
        featured = request.data.get('featured', [])
        restore = request.data.get('restore', [])
        events = Event.objects.filter(uuid__in=featured)
        events.update(status=Event.FEATURED)
        events = Event.objects.filter(uuid__in=restore)
        events.update(status=Event.NONE)
        events = Event.objects.filter(uuid__in=archived)
        events.update(status=Event.ARCHIVED)
        return Response({'message': 'Events Updated'}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def annotate_species(self, request, *args, **kwargs):
        species = request.data.get('species', [])
        species_to_annotate = Specie.objects.filter(id__in=species)
        events_to_edit = request.data.get('events', [])
        for event in Event.objects.filter(uuid__in=events_to_edit):
            event.species.add(*species_to_annotate)
        return Response({'message': 'Species annotated to events'}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def remove_species(self, request, *args, **kwargs):
        species = request.data.get('species', [])
        species = Specie.objects.filter(id__in=species)
        events_to_edit = request.data.get('events', [])
        for event in Event.objects.filter(uuid__in=events_to_edit):
            event.species.remove(*species)
        return Response({'message': 'Removed species from events'}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def delete_events(self, request, *args, **kwargs):
        events = request.data.get('events', [])
        events = Event.objects.filter(uuid__in=events)
        events.delete()
        return Response({'message': 'Deleted events'}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def notify(self, request, *args, **kwargs):
        event = self.get_object()
        send_push_notification(event)
        # message = send_sms("+923009658434", event)
        return Response(event.uuid, status=200)

    @action(methods=['GET'], detail=True)
    def remake(self, request, *args, **kwargs):
        event = self.get_object()
        event.file.delete()
        event.thumbnail.delete()

        with imageio.get_writer(f'{settings.MEDIA_ROOT}/temp/{event.uuid}_thumb.gif', mode='I',
                                duration=0.5) as thumb_writer:
            with imageio.get_writer(f'{settings.MEDIA_ROOT}/temp/{event.uuid}.gif', mode='I', duration=0.5) as writer:
                for image in Image.objects.filter(uuid=event.uuid).order_by('file'):
                    image_data = imageio.imread(image.file.path)

                    for box in BoundingBox.objects.filter(image=image):
                        height, width, _ = image_data.shape
                        x, y, w, h = int(box.x * width), int(box.y * height), int(box.width * width), int(
                            box.height * height)
                        image_data = cv2.rectangle(image_data, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        event.species.add(box.specie)

                    writer.append_data(image_data)
                    thumb_writer.append_data(cv2.resize(image_data, (100, 100)))

        with open(f'media/temp/{event.uuid}.gif', 'rb') as event_gif:
            event.file.save(f'{event.uuid}.gif', File(event_gif), save=True)

        with open(f'media/temp/{event.uuid}_thumb.gif', 'rb') as thumb_gif:
            event.thumbnail.save(f'{event.uuid}.gif', File(thumb_gif), save=True)

        os.remove(f'media/temp/{event.uuid}.gif')
        os.remove(f'media/temp/{event.uuid}_thumb.gif')
        event.save()
        return Response(event.uuid, status=200)


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ImageFilterSet

    def get_queryset(self):
        event_uuid = self.request.query_params.get('event')
        if event_uuid:
            return Image.objects.filter(event__uuid=event_uuid).order_by('date')
        else:
            return Image.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            resp = super(ImageViewSet, self).create(request, *args, **kwargs)
            if 'bbox_data' in request.data:
                boxes = json.loads(request.data['bbox_data'].replace("'", '"'))
                image = Image.objects.filter(id=resp.data['id'])[0]
                for box in boxes:
                    if box['class'] == '0':
                        detection = "smoke"
                    elif box['class'] == '1':
                        detection = "fire"
                    bbox = BoundingBox(image=image, specie_id=detection, **box['box'])
                    bbox.save()
            return resp

        except IntegrityError:
            return Response({'error': 'Duplicate image for this timestamp'}, status=status.HTTP_208_ALREADY_REPORTED)

    @action(methods=['GET'], detail=True)
    def process(self, request, *args, **kwargs):
        image = self.get_object()
        image.boundingbox_set.all().delete()
        image.processed = False
        image.save()
        return self.boxview(request, *args, **kwargs)

    @action(methods=['GET'], detail=True)
    def boxview(self, request, *args, **kwargs):
        image = self.get_object()
        image_data = cv2.imread(f'{settings.BASE_DIR}/media/' + image.file.name)

        for box in BoundingBox.objects.filter(image=image):
            height, width = image_data.shape[:2]
            x, y, w, h = int(box.x * width), int(box.y * height), int(box.width * width), int(box.height * height)
            image_data = cv2.rectangle(image_data, (x, y), (x + w, y + h), (0, 0, 255), 2)

        ret, image_data = cv2.imencode('.png', image_data)
        return HttpResponse(image_data.tobytes(), content_type="image/png")


class BoxViewSet(viewsets.ModelViewSet):
    serializer_class = BoxSerializer
    queryset = BoundingBox.objects.all()
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]
    filterset_fields = {
        'image__date': ['gte', 'lte'],
    }

    @action(methods=['GET'], detail=False)
    def piechart(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        counts = queryset.values('specie__name', 'specie__color').annotate(count=Count("id"))
        pie = {
            'labels': [count['specie__name'] for count in counts],
            'data': [count['count'] for count in counts],
            'colors': [count['specie__color'] for count in counts]
        }
        return Response(pie)

    @action(methods=['GET'], detail=False)
    def linechart(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.values('specie', 'image__date__date').annotate(count=Count('image__date__date')).order_by(
            'image__date__date').values('specie', 'image__date__date', 'count')

        # date_range = self.date_range()
        date_range = sorted(list({str(stat['image__date__date']) for stat in stats}))
        chart = {}

        for specie in Specie.objects.all().values('id', 'name', 'color'):
            counts = [self.stat(specie['id'], date, stats) for date in date_range]

            if not any(counts):
                continue

            chart[specie['id']] = {
                'label': specie['name'],
                'data': counts,
                'backgroundColor': specie['color'],
                'borderColor': specie['color'],
            }

        return Response({'datasets': chart.values(), 'labels': date_range})

    def date_range(self):
        dates = []
        start_date = self.request.GET.get('image__date__gte')
        end_date = self.request.GET.get('image__date__lte')

        today = datetime.now()
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else (
                today - timedelta(days=7)).date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else today.date()

        while start_date <= end_date:
            dates.append(str(start_date))
            start_date += timedelta(days=1)

        return dates

    def stat(self, specie, date, stats):
        for stat in stats:
            if stat['specie'] == specie and str(stat['image__date__date']) == date:
                return stat['count']
        return 0


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [IsAuthenticated]
    res = 0

    def get_object(self):
        if self.request.user.is_superuser:
            return super().get_object()
        return self.request.user.camera

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(organization=self.request.user.organization)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_publish(self, client, userdata, mid):
        if mid > self.res:
            self.res = mid

    def on_log(self, mqttc, obj, level, string):
        return string

    @action(methods=['post'], detail=False)
    def ptzControls(self, request):
        pan = request.data["pan"]
        tilt = request.data["tilt"]
        zoom = request.data["zoom"]
        camera = request.data["camera"]
        client = mqtt.client.Client(clean_session=True, transport="tcp")
        client.tls_set(ca_certs=certifi.where())

        client.on_publish = self.on_publish
        client.on_connect = self.on_connect
        client.on_log = self.on_log

        host = "2be1374228c54154bc14422981467fff.s2.eu.hivemq.cloud"
        client.username_pw_set("admin", "Lumsadmin@n1")
        client.connect(host, 8883, 60)
        client.loop_start()
        client.publish(f"{camera}/PAN", pan, 1)
        client.publish(f"{camera}/TILT", tilt, 1)
        client.publish(f"{camera}/ZOOM", zoom, 1)
        sleep(1)
        client.disconnect()
        client.loop_stop()
        return Response(json.dumps({"data": self.res}))

    @action(methods=['post'], detail=False)
    def ptzControlsOn(self, request):
        pan = request.data["pan"]
        tilt = request.data["tilt"]
        zoom = request.data["zoom"]
        camera = request.data["camera"]
        power = request.data.get("power", "on")
        message = request.data["message"]
        client = mqtt.client.Client(clean_session=True, transport="tcp")
        client.tls_set(ca_certs=certifi.where())

        client.on_publish = self.on_publish
        client.on_connect = self.on_connect
        client.on_log = self.on_log

        host = "2be1374228c54154bc14422981467fff.s2.eu.hivemq.cloud"
        client.username_pw_set("admin", "Lumsadmin@n1")
        client.connect(host, 8883, 60)
        client.loop_start()
        client.publish(f"{camera}/PAN", pan, 1)
        client.publish(f"{camera}/TILT", tilt, 1)
        client.publish(f"{camera}/ZOOM", zoom, 1)
        if power.lower() == "on":
            client.publish(f"{camera}/POWER", "ON", 1)
        elif power.lower() == "off":
            client.publish(f"{camera}/POWER", "OFF", 1)
        sleep(1)
        client.disconnect()
        client.loop_stop()
        return Response(json.dumps({"data": self.res}))

    @action(methods=['POST'], detail=False)
    def live_update(self, request, *args, **kwargs):
        cam_id = request.POST['cam_id']
        live_image = request.FILES['file']
        Camera.objects.filter(id=cam_id).update(live_image=f'liveimages/cam_{cam_id}_live_image')
        fs = FileSystemStorage(location='media/liveimages')
        if fs.exists(f'cam_{cam_id}_live_image'):
            fs.delete(f'cam_{cam_id}_live_image')
        fs.save(f'cam_{cam_id}_live_image', live_image)
        return Response({'message': f'live image updated for camera {cam_id}'}, status=status.HTTP_200_OK)


class EventCountViewSet(viewsets.ModelViewSet):
    queryset = EventCount.objects.all()
    serializer_class = EventCountSerializer

    def get_queryset(self):
        # Assuming you have a request parameter 'camera_id' that specifies the camera ID
        camera_id = self.request.query_params.get('camera')
        if camera_id:
            return EventCount.objects.filter(camera=camera_id)
        else:
            return EventCount.objects.all()

    @action(methods=['POST'], detail=False)
    def delete_events(self, request, *args, **kwargs):
        events = request.data.get('events', [])
        events = Event.objects.filter(uuid__in=events)
        events.delete()

        # Update EventCount after deletion
        updated_event_count = Event.objects.count()
        event_count_instance, _ = EventCount.objects.get_or_create(
            id=1)  # Assuming there's only one instance of EventCount
        event_count_instance.count = updated_event_count
        event_count_instance.save()

        return Response({'message': 'Deleted events and updated EventCount'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'EventCount deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class OrganizationViewSet(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.organization


class ReadingViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingSerializer
    queryset = Reading.objects.all()
    permission_classes = [IsAuthenticated]


class LogViewSet(viewsets.ModelViewSet):
    serializer_class = LogSerializer
    queryset = Log.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PTZCameraPresetListCreateAPIView(viewsets.ModelViewSet):
    queryset = PTZCameraPreset.objects.all()
    serializer_class = PTZCameraPresetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PTZCameraPresetDetailAPIView(viewsets.ModelViewSet):
    queryset = PTZCameraPreset.objects.all()
    serializer_class = PTZCameraPresetSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        camera_id = self.request.query_params.get('camera_id')
        if camera_id is not None:
            queryset = queryset.filter(camera_id=camera_id)
        return queryset


class WeatherDataAPIView(viewsets.ModelViewSet):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    pagination_class = DynamicPagination
    def get_queryset(self):
        queryset = super().get_queryset()

        # Get the query parameters
        camera_id = self.request.query_params.get('camera_id')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        # Filter by camera_id if provided
        if camera_id is not None:
            queryset = queryset.filter(camera_id=camera_id)

        # Filter by start_time and end_time if provided
        if start_time:
            start_time = parse_datetime(start_time)  # Convert to datetime object
            if start_time:
                queryset = queryset.filter(timestamp__gte=start_time)

        if end_time:
            end_time = parse_datetime(end_time)  # Convert to datetime object
            if end_time:
                queryset = queryset.filter(timestamp__lte=end_time)

        return queryset
