from django.urls import path, include


urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    # path('signup/', views.signup, name='signup'),
    path('api/', include('djoser.urls'), name='auth_api'),
    path('api/', include('djoser.urls.authtoken')),
    path('api/', include(('accounts.api.urls', 'accounts'), namespace='accounts-api')),
]
