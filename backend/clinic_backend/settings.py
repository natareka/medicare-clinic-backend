"""
Django Settings for MediCare Clinic Booking System
Compatible with Windows & Mac
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production-use-strong-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', '0.0.0.0']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'clinic',
]

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

ROOT_URLCONF = 'clinic_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'clinic_backend.wsgi.application'

# ─── DATABASE (MySQL) ──────────────────────────────────────────────────────────
# This setup works for BOTH your local computer and Render.com
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'defaultdb'),
        'USER': os.environ.get('DB_USER', 'avnadmin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'AVNS_9YxGzQ4A3IYp2IHePsr'),
        'HOST': os.environ.get('DB_HOST', '143.110.244.31'),
        'PORT': os.environ.get('DB_PORT', '25488'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", 
            'ssl': {
                # This automatically finds the ca.pem file in your project folder
                'ca': os.path.join(BASE_DIR, 'ca.pem') 
            },
        },
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'defaultdb',
#         'USER': 'avnadmin',
#         'PASSWORD': 'YOUR_PASSWORD_FROM_SCREEN',
#         'HOST': 'mysql-3e6de62b-rekamca7-b54d.l.aivencloud.com',
#         'PORT': '25488',
#         'OPTIONS': {
#             'ssl': {'ca': '/path/to/ca.pem'}, # See Step 2 below
#         },
#     }
# }
# ─── EMAIL SETTINGS (Gmail SMTP) ──────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'rekamca7@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ecjbhjhlahzbmapx')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', 'noreply@medicare-clinic.com')
EMAIL_FROM_NAME = 'MediCare Clinic'

# ─── SMS SETTINGS (Twilio) ────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'AC310f21fa19213ebd47b30e3ad7a6624d')
TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN',  '8ca9dca4abafe7680cb1eefff85f7e40')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '+16624957616')

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5500",
#     "http://127.0.0.1:5500",
#     "http://localhost:8000",
# ]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",        # If testing locally
    "http://127.0.0.1:5500",        # For VS Code Live Server
    "https://your-frontend.render.com" # If hosted
    "[https://medicare-clinic-backend-1.onrender.com](https://medicare-clinic-backend-1.onrender.com)"
]

# ─── REST FRAMEWORK ───────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Singapore'
USE_I18N = True
USE_TZ = True

# STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# ─── STATIC FILES (REQUIRED FOR HOSTING) ──────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Add this for Render hosting so your CSS/Images work
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Make sure 'whitenoise.middleware.WhiteNoiseMiddleware' is in your MIDDLEWARE
# Place it right after SecurityMiddleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'clinic.log',
        },
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'clinic': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
