from django.urls import path
from rest_framework import routers

from .api_views import ImageViewSet, BoxViewSet, CameraViewSet, ReadingViewSet, LogViewSet, EventViewSet, \
    OrganizationViewSet

router = routers.DefaultRouter()
router.register('image', ImageViewSet)
router.register('event', EventViewSet)
router.register('box', BoxViewSet)
router.register('reading', ReadingViewSet)
router.register('camera', CameraViewSet)
# router.register('organization', OrganizationViewSet)
router.register('logs', LogViewSet)

urlpatterns = []

urlpatterns += router.urls

urlpatterns += [path('organization/', OrganizationViewSet.as_view())]
