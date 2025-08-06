import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-dev')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# For Vercel deployment, the allowed host will be '.vercel.app'
ALLOWED_HOSTS = ['127.0.0.1', '.vercel.app']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',  # For django-storages (Cloudflare R2)
    # Our apps
    'apps.authentication',
    'apps.dashboard',
    'apps.billing',
    'apps.social',
    'core',
]

# Use our custom User model
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        # ... context processors
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# --- DATABASE CONFIGURATION (for PostgreSQL) ---
# Vercel will provide the DATABASE_URL environment variable.
# dj_database_url parses it into the correct format for Django.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# --- CLOUDFLARE R2 STORAGE CONFIGURATION ---
# These settings tell django-storages how to connect to your R2 bucket.
# All these values should be set as environment variables in Vercel.
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN') # e.g., 'media.yourdomain.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = None
AWS_LOCATION = 'static' # A sub-folder in your bucket for static files

# Tell Django to use R2 for storing both static files and user-uploaded media files.
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/" if AWS_S3_CUSTOM_DOMAIN else f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_LOCATION}/"


# --- Standard Django Settings ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
