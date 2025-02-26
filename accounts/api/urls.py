from django.urls import path, get_resolver
from rest_framework import routers
from accounts.views import send_reset_password_email, reset_password_confirm

router = routers.DefaultRouter()

urlpatterns = []

urlpatterns += router.urls

urlpatterns += [
    path('send-reset-password/', send_reset_password_email, name='send-reset-password'),
    path('reset-password-confirm/', reset_password_confirm, name='reset-password-confirm'),
]
