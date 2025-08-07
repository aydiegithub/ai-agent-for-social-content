import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# --- Core Settings ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')

# DEBUG should always be False in production for security and performance.
# We default to 'False' and only set it to True if the env var is explicitly 'True'.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS is critical for security.
# In production on Cloud Run, you should set this to your custom domain.
# e.g., 'www.your-domain.com,your-app-name.a.run.app'
# For now, we can use a flexible approach.
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# CSRF protection needs to trust your production domain.
CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1').split(',')


# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # More efficient static file serving
    'django.contrib.staticfiles',
    'storages',  # For django-storages (Cloudflare R2)
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


# --- Database Configuration (for Aiven PostgreSQL) ---
# In production, GCP/Cloud Run will provide the DATABASE_URL environment variable.
# dj_database_url parses it into the correct format for Django.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600, # Keeps connections alive for performance
        ssl_require=os.getenv('DATABASE_SSL_REQUIRE', 'False') == 'True'
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

# Static files (CSS, JavaScript, Images) are served by WhiteNoise.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User-generated content like AI images) are stored on Cloudflare R2.
# These settings tell django-storages how to connect to your R2 bucket.
# All these values will be set as environment variables in production.
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN') # e.g., 'media.yourdomain.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = 'public-read' # Make files publicly accessible

# This tells Django to use our R2 bucket for any file uploads.
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# --- Production Security Settings ---
# These are ignored if DEBUG is True.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # You may need to configure SECURE_PROXY_SSL_HEADER if you're behind a proxy
    # that terminates SSL, which Cloud Run does.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')