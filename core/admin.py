from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from import_export.admin import ExportActionMixin
from django.utils.timezone import localtime
from core.filters import SpecieFilter, CameraFilter
from core.models import Specie, Camera, Image, BoundingBox, Slot, Event, Log, DontCare, Tower, Sensor, PTZCameraPreset


class SpecieAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'endangered', 'enabled')
    search_fields = ('id', 'name',)
    list_filter = ('endangered', 'enabled')


class SlotAdminInline(admin.TabularInline):
    model = Slot
    extra = 0


class TowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lat', 'lng',)
    search_fields = ('id', "name",)


class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tower', 'sensor_type')
    list_filter = ("sensor_type",)
    search_fields = ('id', 'name', "tower", "sensor_type")


class DontCareAdminInline(admin.TabularInline):
    model = DontCare
    extra = 0


class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'user', 'live', 'should_log', 'contact_no', 'latitude', 'longitude', 'confidence_threshold',)
    search_fields = ('id', 'latitude', 'longitude',)
    inlines = [SlotAdminInline, DontCareAdminInline]
    actions = ['turn_logging_on', 'turn_logging_off', 'start_capture', 'stop_capturing']

    fieldsets = [
        (None, {'fields': ['test', 'live', 'should_log', 'description', 'user', 'organization', 'tower', 'live_image','live_stream_url']}),
        ('Stats', {'fields': ['last_reported_at', 'remaining_storage']}),
        ('Capture Settings', {'fields': ['frames_per_sec', 'image_width', 'image_height', 'roi_mask']}),
        ('Thresholds', {'fields': ['day_threshold', 'night_threshold', 'iou_threshold', 'confidence_threshold']}),
        ('Site', {'fields': ['latitude', 'longitude', 'sunrise', 'sunset', 'contact_no']}),
        ('Pins', {'fields': ['infrared', 'pwm', 'filter_a', 'filter_b', 'motion_1', 'motion_2', 'pin_4g']}),
        ('Intervals', {'fields': ['update_after', 'video_interval', 'rest_interval', 'motion_interval', 'idol_4g_interval']}),
    ]

    def turn_logging_on(self, request, queryset):
        queryset.update(should_log=True)

    def turn_logging_off(self, request, queryset):
        queryset.update(should_log=False)

    def start_capture(self, request, queryset):
        queryset.update(live=True)

    def stop_capturing(self, request, queryset):
        queryset.update(live=False)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'processed', 'included', 'date', 'event', 'camera', "link_to_actions", 'box_view')
    list_filter = (SpecieFilter, 'camera__id', 'included')
    search_fields = ('event__uuid',)

    def link_to_actions(self, obj):
        if obj.processed:
            return format_html('<a href="{}" target="_blank">Reprocess</a>', reverse("core:core-api:image-process", args=[obj.id]))
        return format_html('<a href="{}" target="_blank">Process</a>', reverse("core:core-api:image-process", args=[obj.id]))

    def box_view(self, obj):
        return format_html(f'<a href={reverse("core:core-api:image-boxview", args=[obj.id])} target="_blank">BoxView</a>')


class EventAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'file', 'date', 'specie_list', 'sms_sent')
    list_filter = (CameraFilter, 'species', 'status')
    search_fields = ('uuid',)

    def specie_list(self, obj):
        return '|'.join(obj.species.all().values_list('name', flat=True))


class FieldImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'device', 'created_at', 'view')
    list_filter = (CameraFilter,)
    search_fields = ('name',)

    def device(self, obj):
        return f'{obj.camera.id} | {obj.camera.description}'

    def view(self, obj):
        return format_html(f'<a href="{obj.file.url}" target="_blank">View</a>')


class BoundingBoxAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'image', 'specie', 'x', 'y', 'width', 'height',)
    list_filter = ('specie__id', 'specie__endangered',)
    search_fields = ('specie__id', 'specie__name',)

    def image_id(self, obj):
        return obj.image.id


class LogAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('message', 'activity', 'logged_at_sec', 'script', 'camera')
    list_filter = (CameraFilter, 'activity', 'script')

    def logged_at_sec(self, obj):
        return localtime(obj.logged_at).strftime("%b %d, %Y %H:%M:%S")

    logged_at_sec.short_description = 'Logged At'

class PTZCameraPresetAdmin(admin.ModelAdmin):
    list_display = ('camera_id', 'name', 'zoom_min', 'zoom_max', 'zoom_default', 'pan_min', 'pan_max', 'pan_default', 'tilt_min', 'tilt_max', 'tilt_default')
    list_filter = ('camera_id', 'name')
    search_fields = ('camera_id', 'name')

admin.site.register(Camera, CameraAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Specie, SpecieAdmin)
admin.site.register(BoundingBox, BoundingBoxAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Tower, TowerAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(PTZCameraPreset, PTZCameraPresetAdmin)


