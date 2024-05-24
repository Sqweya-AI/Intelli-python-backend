# MAIN_PROJECT/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG')

#MYSQL
DB_ENGINE = os.getenv('DB_ENGINE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

#POSTGRES
POSTGRES_DB_ENGINE = os.getenv('POSTGRES_DB_ENGINE')
POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_DB_PORT = os.getenv('POSTGRES_DB_PORT')
POSTGRES_DOCKER_DB_HOST = os.getenv('POSTGRES_DOCKER_DB_HOST')



#DEFAULT DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# POSTGRES_USER=POSTGRES_DB_USER
# POSTGRES_PASSWORD=POSTGRES_DB_PASSWORD
# POSTGRES_DB=POSTGRES_DB_NAME


# DATABASES
# RENDER POSTGRESS
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL'), #from render postgres
#         conn_max_age=600
#     )
# }


# #postgres-local-db
# DATABASES = {
#     'default': {
#         'ENGINE': POSTGRES_DB_ENGINE,
#         'NAME': POSTGRES_DB_NAME,
#         'USER': POSTGRES_DB_USER,
#         'PASSWORD' : POSTGRES_DB_PASSWORD,
#         'HOST': POSTGRES_DB_HOST, 
#         'PORT': POSTGRES_DB_PORT
#     }
# }

# #postgres-docker-db
# DATABASES = {
#     'default': {
#         'ENGINE': POSTGRES_DB_ENGINE,
#         'NAME': POSTGRES_DB_NAME,
#         'USER': POSTGRES_DB_USER,
#         'PASSWORD' : POSTGRES_DB_PASSWORD,
#         'HOST': POSTGRES_DOCKER_DB_HOST, 
#         'PORT': POSTGRES_DB_PORT
#     }
# }




# ALLOWED_HOSTS = ['https://intelli-python-backend.onrender.com', 'localhost']
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True


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
    'main_app',
    'auth_app',
    'bot_app',
    'dashboard_app',
    'billing_app',
    'corsheaders',
]

# CORS_ALLOWED_ORIGINS = [
#     'http://*',
#     'https://*',
# ]
# Allow all origins



# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
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
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'path.to.YourCustomAuthBackend',
]
EMAIL_BACKEND = 'resend.backend.ResendBackend'

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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'


if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
























# STORE
# REST_FRAMEWORK = {
    
# }

# REST_FRAME = {
#     # ... other settings
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#     ],
#     'DEFAULT_PARSER_CLASSES': [
#         'rest_framework.parsers.JSONParser',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.SessionAuthentication',
#     ],
#     'EXCEPTION_HANDLER': 'yourapp.exception_handler.custom_exception_handler',  # Optional: Custom exception handler (replace 'yourapp' with your app name)
# }


# emailing/ no env variables yet
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'saadatsamjo@gmail.com'
# EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxxxxxxx!'


# # Custom mySQL 
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'chatbotappDB',
#         'USER': 'root',
#         'PASSWORD': DB_PASSWORD,
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'IntelliPostgresDB',
#         'USER':'postgres',
#         'PASSWORD' : 'abcd',
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
