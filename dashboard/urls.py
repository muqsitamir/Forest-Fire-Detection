from django.urls import path,include
from .views import *
from django.contrib import admin
urlpatterns = [
    path('ptzControlsHawa',PTZControlsHawa.as_view(),name='ptzControlsHawa'),
    path('ptzControlsPanja',PTZControlsPanja.as_view(),name='ptzControlsPanja'),
    path('ptzControlsPalm',PTZControlsPalm.as_view(),name='ptzControlsPalm'),
]