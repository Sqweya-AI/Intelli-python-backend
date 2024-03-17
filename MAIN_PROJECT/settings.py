# MAIN_PROJECT/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DEBUG = True


# Custom mySQL 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chatbotappDB',
        'USER': 'root',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'path.to.YourCustomAuthBackend',
]

# Application definition
INSTALLED_APPS = [
   'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'auth_app',
    'bot_app'  
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MAIN_PROJECT.urls'
AUTH_USER_MODEL = 'auth_app.User'



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
WSGI_APPLICATION = 'MAIN_PROJECT.wsgi.application'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# STORE
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
# }

# emailing/ no env variables yet
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'saadatsamjo@gmail.com'
# EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxxxxxxx!'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'chatbotappDB',
#         'USER':'postgres',
#         'PASSWORD' : '1111',
#         'HOST':'localhost',
#         'PORT': 5432
#     }
# }


# MongoDB configuration
# MONGODB_HOST = 'localhost'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django_mongodb_engine',
#         'NAME': db.name,
#         'HOST': MONGODB_HOST,
#         'USER': '',
#         'PASSWORD': '',
#         'AUTH_SOURCE': '$external',
#         'AUTH_MECHANISM': 'MONGODB-CR',
#         'PORT': 27017,
#         'ENFORCE_SCHEMA': False,
#     }
# }
# MIGRATION_MODULES = {}
# UNSAFE
