from django.urls import path, include
from accounts.api.api_views import PasswordResetView, PasswordChangeView

from . import views

urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    # path('signup/', views.signup, name='signup'),
    path('api/', include('djoser.urls'), name='auth_api'),
    path('api/', include('djoser.urls.authtoken')),
    path('api/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password/change/', PasswordChangeView.as_view(), name='password_change'),

]
