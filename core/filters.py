from django.contrib import admin

from core.models import Specie, Camera


class SpecieFilter(admin.SimpleListFilter):
    title = 'Specie'
    parameter_name = 'specie'

    def lookups(self, request, model_admin):
        return ((specie.id, specie.name) for specie in
                Specie.objects.all())

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.distinct().filter(boundingbox__specie=value)
        return queryset


class CameraFilter(admin.SimpleListFilter):
    title = 'Camera'
    parameter_name = 'camera'

    def lookups(self, request, model_admin):
        return ((camera.id, f'{camera.id} | {camera.description}') for camera in
                Camera.objects.all())

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.distinct().filter(camera__id=value)
        return queryset
