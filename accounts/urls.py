from django.urls import path, include

from . import views

urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    # path('signup/', views.signup, name='signup'),
    path('api/', include('djoser.urls'), name='auth_api'),
    path('api/', include('djoser.urls.authtoken')),
]
