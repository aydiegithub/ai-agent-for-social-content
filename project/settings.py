import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# --- Core Settings ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
# DEBUG should be False in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# GCP Cloud Run provides the PORT environment variable.
ALLOWED_HOSTS = ['*'] # Cloud Run handles host security.


# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',  # For django-storages
    # Our apps
    'apps.authentication',
    'apps.dashboard',
    'apps.billing',
    'apps.social',
    'core',
]

AUTH_USER_MODEL = 'authentication.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'


# --- Database Configuration (for Google Cloud SQL) ---
# GCP will provide the DATABASE_URL environment variable.
# dj_database_url will parse it into the correct format for Django.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}


# --- Templates & Internationalization ---
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Static & Media Files Configuration ---

# This is the folder where Django will collect all static files during the build.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# This tells Django to use Whitenoise to serve static files efficiently.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Cloudflare R2 for Media Files (Generated Images) ---
# These settings tell django-storages how to connect to your R2 bucket.
# All these values should be set as environment variables in GCP.
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN') # e.g., 'media.yourdomain.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = None

# This tells Django to use our R2 bucket for any file uploads.
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'