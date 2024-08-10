"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hu&_2(m@8zt3_m7rgihu6za5ed47vxt#f9m&-ds^i+&55fn3q0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['172.105.61.72', 'api.forestwatch.org.pk', "*"]

ALLOWED_HOSTS += ['127.0.0.1', '192.168.0.12', "139.162.11.234"]
# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_cron',
    'djoser',
    'fcm_django',
    'webpack_loader',
    'corsheaders',
]

CUSTOM_APPS = [
    'accounts',
    'core'
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/accounts/login/'

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'new-password/{uid}/{token}',
    'ACTIVATION_URL': 'verify-email/{uid}/{token}',
    'SERIALIZERS': {
        'token': 'accounts.api.serializers.CustomTokenSerializer',
        'current_user': 'accounts.api.serializers.CurrentUserSerializer',
    },
    'TOKEN_MODEL': 'rest_framework.authtoken.models.Token',
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CRON_CLASSES = [
    "cronjobs.process_images.ProcessImagesCronJob",
    "cronjobs.process_events.ProcessEventsCronJob",
    "cronjobs.set_sun_times.SetSunTimesCronJob",
    #"cronjobs.parse_kmz.ParseKMZCronJob",
    #"cronjobs.download_kmz.DownloadKMZCronJob",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
       'http://127.0.0.1:8000',
       'https://forestwatch.org.pk',
)
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:3000',
    "https://forestwatch.org.pk",
]
CORS_PREFLIGHT_MAX_AGE = 86400  # 1 day

CORS_ALLOW_HEADERS = (
    'access-control-allow-origin',
    'content-type',
    'authorization',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'forest_fire',
        'USER': 'root',
        'PASSWORD': 'fif_607_taj',
        'HOST': '139.162.11.234',
        'PORT': '3306',
    }
}


FCM_DJANGO_SETTINGS = {
    # default: _('FCM Django')
    # "APP_VERBOSE_NAME": "[string for AppConfig's verbose_name]",
    # Your firebase API KEY
    "FCM_SERVER_KEY": "AAAA4-iM2xE:APA91bGlAptzvSvK2h2WIZDSdF5dwkAf6zjqeiEWIVST8irAl3FN7iwakzr51Se1"
                      "OFsdojGBDMYeOelQlldAyCL8uU3zAYpPre18K___ju7husgPdc93gnWDi_rqlt8WddLDVHxru9aI",
    # true if you want to have only one active device per registered user at a time
    # default: False
    # "ONE_DEVICE_PER_USER": True/False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    # "DELETE_INACTIVE_DEVICES": True/False,
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'accounts.User'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

MODEL_SERVICE_URL = 'http://203.135.63.37:5000'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'lumscameratrap@gmail.com'
EMAIL_HOST_PASSWORD = 'xzwr fguu icqv jxlv'
DEFAULT_FROM_EMAIL = "lumscameratrap@gmail.com"


