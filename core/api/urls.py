from django.urls import path
from rest_framework import routers

from .api_views import ImageViewSet, BoxViewSet, CameraViewSet, ReadingViewSet, LogViewSet, EventViewSet, \
    OrganizationViewSet, TowerViewSet, PTZCameraPresetDetailAPIView, EventCountViewSet,WeatherDataAPIView

router = routers.DefaultRouter()
router.register('image', ImageViewSet)
router.register('event', EventViewSet)
router.register('box', BoxViewSet)
router.register('reading', ReadingViewSet)
router.register('camera', CameraViewSet)
router.register('eventcount', EventCountViewSet)
# router.register('organization', OrganizationViewSet)
router.register('logs', LogViewSet)
router.register('towers', TowerViewSet)
router.register('preset',PTZCameraPresetDetailAPIView)
router.register('weatherdata',WeatherDataAPIView)

urlpatterns = []

urlpatterns += router.urls

urlpatterns += [path('organization/', OrganizationViewSet.as_view())]
