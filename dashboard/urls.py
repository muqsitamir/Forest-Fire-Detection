from django.urls import path,include
from .views import *
from django.contrib import admin
urlpatterns = [
    #path('login',loginUser),
    path('register',userform.as_view(),name='register'),
    path('login',LoginUserForm.as_view(),name='login'),
    path('cameras',CameraList.as_view(),name='cameras'),
    path('sensors',SensorList.as_view(),name='sensors'),
    path('towerDetails',TowerDetailList.as_view(),name='towerDetails'),
    path('towers',TowerList.as_view(),name='towers'),
    path('events',EventList.as_view(),name='events'),
]