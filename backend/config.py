#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
from datetime import timedelta

# Pip package imports
import redis
from appdirs import AppDirs
from flask_mm.postprocess import Watermarker

# Internal package imports
from backend.utils.date import utcnow

# Application name and directory setup
APP_NAME = 'flask-starter'
app_dirs = AppDirs(APP_NAME)
APP_CACHE_FOLDER = app_dirs.user_cache_dir
APP_DATA_FOLDER = app_dirs.user_data_dir

# Flask assets folder setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'backend', 'templates')
STATIC_FOLDER = os.environ.get('FLASK_STATIC_FOLDER', os.path.join(PROJECT_ROOT, 'static'))

STATIC_URL_PATH = '/static' # serve asset files in static/ at /static/

# blog articles configuration
# ARTICLES_FOLDER = os.path.join(PROJECT_ROOT, 'articles')
# ARTICLE_PREVIEW_LENGTH = 400
# FRONTMATTER_LIST_DELIMETER = ','
# MARKDOWN_EXTENSIONS = ['extra']
# DEFAULT_ARTICLE_AUTHOR_EMAIL = 'a@a.com'
# SERIES_FILENAME = 'series.md'
# ARTICLE_FILENAME = 'article.md'
# ARTICLE_STYLESHEET_FILENAME = 'styles.css'

# list of bundle modules to register with the app, in dot notation
BUNDLES = [
    'backend.contrib.admin',
    #'backend.blog',
    'backend.contrib.security',
    'backend.contrib.contact_submission',
    'backend.contrib.newsletter_subscribe',
    'backend.shop',
    'backend.site',

    'backend.contrib.test_file',
    #'backend.site',
]

# ordered list of extensions to register before the bundles
# syntax is import.name.in.dot.module.notation:extension_instance_name
EXTENSIONS = [
    'backend.extensions:session',               # should be first
    'backend.extensions:csrf',                  # should be second
    'backend.extensions:db',
    'backend.extensions:alembic',               # must come after db
    'backend.extensions.celery:celery',
    'backend.extensions.mail:mail',
    'backend.extensions.marshmallow:ma',        # must come after db
    'backend.extensions.security:security',     # must come after celery and mail
    'backend.extensions.debug:toolbar',
    'backend.extensions.mediamanager:storage',
    'backend.extensions.stripe:stripe',
]

# list of extensions to register after the bundles
# syntax is import.name.in.dot.module.notation:extension_instance_name
DEFERRED_EXTENSIONS = [
    'backend.extensions.api:api',
    'backend.extensions.admin:admin',
]


def get_boolean_env(name, default):
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in ['true', 'yes', '1']


class BaseConfig(object):
    ##########################################################################
    # flask                                                                  #
    ##########################################################################
    DEBUG = get_boolean_env('FLASK_DEBUG', False)
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'not-secret-key')  # FIXME
    STRICT_SLASHES = False
    BUNDLES = BUNDLES

    ##########################################################################
    # session/cookies                                                        #
    ##########################################################################
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(os.environ.get('REDISCLOUD_URL')) if 'REDISCLOUD_URL' in os.environ else redis.Redis(
        host=os.getenv('FLASK_REDIS_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_REDIS_PORT', 6379)),
    )
    SESSION_PROTECTION = 'strong'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # SECURITY_TOKEN_MAX_AGE is fixed from time of token generation;
    # it does not update on refresh like a session timeout would. for that,
    # we set (the ironically named) PERMANENT_SESSION_LIFETIME
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    ##########################################################################
    # database                                                               #
    ##########################################################################
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALEMBIC = {
        'script_location': os.path.join(PROJECT_ROOT, 'migrations'),
    }

    ##########################################################################
    # celery                                                                 #
    ##########################################################################
    CELERY_BROKER_URL = 'redis://{host}:{port}/0'.format(
        host=os.getenv('FLASK_REDIS_HOST', '127.0.0.1'),
        port=os.getenv('FLASK_REDIS_PORT', 6379),
    )
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ('json', 'pickle')

    ##########################################################################
    # mail                                                                   #
    ##########################################################################
    MAIL_ADMINS = ('admin@example.com',)  # FIXME
    MAIL_SERVER = os.environ.get('FLASK_MAIL_HOST', 'localhost')
    MAIL_PORT = int(os.environ.get('FLASK_MAIL_PORT', 25))
    MAIL_USE_TLS = get_boolean_env('FLASK_MAIL_USE_TLS', False)
    MAIL_USE_SSL = get_boolean_env('FLASK_MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('FLASK_MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('FLASK_MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = (
        os.environ.get('FLASK_MAIL_DEFAULT_SENDER_NAME', 'Fairy Light'),
        os.environ.get('FLASK_MAIL_DEFAULT_SENDER_EMAIL',
                       f"noreply@{os.environ.get('FLASK_DOMAIN', 'localhost')}")
    )

    ##########################################################################
    # CSRF token lifetime                                                    #
    ##########################################################################
    WTF_CSRF_TIME_LIMIT = None

    ##########################################################################
    # security                                                               #
    ##########################################################################
    SECURITY_DATETIME_FACTORY = utcnow

    # specify which user field attributes can be used for login
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email', 'username']

    # NOTE: itsdangerous "salts" are not normal salts in the cryptographic
    # sense, see https://pythonhosted.org/itsdangerous/#the-salt
    SECURITY_PASSWORD_SALT = os.environ.get('FLASK_SECURITY_PASSWORD_SALT',
                                            'security-password-salt')

    # disable flask-security's use of .txt templates (instead we
    # generate the plain text from the html message)
    SECURITY_EMAIL_PLAINTEXT = False

    # enable forgot password functionality
    SECURITY_RECOVERABLE = True

    # enable email confirmation before allowing login
    SECURITY_CONFIRMABLE = True

    # this setting is parsed as a kwarg to timedelta, so the time unit must
    # always be plural
    SECURITY_CONFIRM_EMAIL_WITHIN = '7 days'  # default 5 days

    # urls for the *frontend* router
    SECURITY_CONFIRM_ERROR_VIEW = '/sign-up/resend-confirmation-email'
    SECURITY_POST_CONFIRM_VIEW = '/?welcome'

    ##########################################################################
    # debug                                                               #
    ##########################################################################
    # This mut be set to False during testing
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    ##########################################################################
    # Stripe - Payment                                                       #
    ##########################################################################
    STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
    STRIPE_WEBHOOK_SECRET = os.environ['STRIPE_WEBOOK_SECRET']
    STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']

class ProdConfig(BaseConfig):
    ##########################################################################
    # flask                                                                  #
    ##########################################################################
    SERVER_NAME = os.environ.get('SERVER_NAME', 'fairy-light.herokuapp.com')
    ENV = 'prod'
    DEBUG = get_boolean_env('FLASK_DEBUG', False)

    ##########################################################################
    # database                                                               #
    ##########################################################################
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=os.environ.get('FLASK_DATABASE_USER', 'flask_api'),
        password=os.environ.get('FLASK_DATABASE_PASSWORD', 'flask_api'),
        host=os.environ.get('FLASK_DATABASE_HOST', '127.0.0.1'),
        port=os.environ.get('FLASK_DATABASE_PORT', 5432),
        db_name=os.environ.get('FLASK_DATABASE_NAME', 'flask_api'),
    ))

    ##########################################################################
    # session/cookies                                                        #
    ##########################################################################
    SESSION_COOKIE_DOMAIN = os.environ.get('FLASK_DOMAIN', 'fairy-light.herokuapp.com')
    SESSION_COOKIE_SECURE = get_boolean_env('SESSION_COOKIE_SECURE', True)

    # SECURITY_TOKEN_MAX_AGE is fixed from time of token generation;
    # it does not update on refresh like a session timeout would. for that,
    # we set (the ironically named) PERMANENT_SESSION_LIFETIME
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    ##########################################################################
    # Flask FS - FileSystem                                            #
    ##########################################################################
    # Whether or not image should be compressedd/optimized by default.
    FS_IMAGES_OPTIMIZE = True

    ##########################################################################
    # Flask MM - MediaManager                                            #
    ##########################################################################
    # The global local storage root.
    MM_AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    MM_AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    MM_AWS_REGION = os.environ.get('AWS_REGION')
    MM_BUCKET_NAME = os.environ.get('BUCKET_NAME', 'fairy-light')
    MM_PHOTO = {
        'ROOT': 'photo',
        'PREFIX': '/photo',  # Serving file from S3 is not yet supported
        'STORAGE': 's3',
        'MANAGER': 'image',
        'THUMBNAIL_SIZE': (253, 220, True),  # Generate strict thumbnails
        'MAX_SIZE': (1280, 1720, False),  # Optimise the image size for the watermarked image
        'POSTPROCESS': Watermarker(os.path.join(STATIC_FOLDER, 'site', 'img', 'wm_fllogof_rs.png'), position='c'),
    }

    MM_PRODUCT = {
        'ROOT': 'product',
        'PREFIX': '/product',  # Serving file from S3 is not yet supported
        'STORAGE': 's3',
        'MANAGER': 'image',
        'THUMBNAIL_SIZE': None,  # Do not generate thumbnails
    }

class DevConfig(BaseConfig):
    ##########################################################################
    # flask                                                                  #
    ##########################################################################
    ENV = 'dev'
    DEBUG = get_boolean_env('FLASK_DEBUG', True)
    #SERVER_NAME = 'localhost:5000'
    # EXPLAIN_TEMPLATE_LOADING = True

    ##########################################################################
    # session/cookies                                                        #
    ##########################################################################
    SESSION_COOKIE_SECURE = False

    # SECURITY_TOKEN_MAX_AGE is fixed from time of token generation;
    # it does not update on refresh like a session timeout would. for that,
    # we set (the ironically named) PERMANENT_SESSION_LIFETIME
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    ##########################################################################
    # database                                                               #
    ##########################################################################
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=os.environ.get('FLASK_DATABASE_USER', 'flask_api'),
        password=os.environ.get('FLASK_DATABASE_PASSWORD', 'flask_api'),
        host=os.environ.get('FLASK_DATABASE_HOST', '127.0.0.1'),
        port=os.environ.get('FLASK_DATABASE_PORT', 5432),
        db_name=os.environ.get('FLASK_DATABASE_NAME', 'flask_api'),
    )
    # SQLALCHEMY_ECHO = True

    ##########################################################################
    # mail                                                                   #
    ##########################################################################
    MAIL_PORT = 1025  # MailHog
    MAIL_DEFAULT_SENDER = ('Flask-starter', 'noreply@localhost')

    ##########################################################################
    # security                                                               #
    ##########################################################################
    SECURITY_CONFIRMABLE = True
    SECURITY_CONFIRM_EMAIL_WITHIN = '1 minutes'  # for testing
    ##########################################################################
    # debug                                                               #
    ##########################################################################
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True

    ##########################################################################
    # Flask FS - FileSystem                                            #
    ##########################################################################
    # Whether or not image should be compressedd/optimized by default.
    FS_IMAGES_OPTIMIZE = False

    ##########################################################################
    # Flask MM - MediaManager                                            #
    ##########################################################################
    # The global local storage root.
    MM_PHOTO = {
        'ROOT': os.path.join(STATIC_FOLDER, 'photo'),
        'PREFIX': '/photo',  # Serving file from S3 is not yet supported
        'STORAGE': 'local',
        'MANAGER': 'image',
        'THUMBNAIL_SIZE': (253, 220, True),  # Generate strict thumbnails
        'MAX_SIZE': (1280, 1720, False),  # Optimise the image size for the watermarked image
        'POSTPROCESS': Watermarker(os.path.join(STATIC_FOLDER, 'site', 'img', 'wm_fllogof_rs.png'), position='c'),
    }

    MM_PRODUCT = {
        'ROOT': os.path.join(STATIC_FOLDER, 'product'),
        'PREFIX': '/product',  # Serving file from S3 is not yet supported
        'STORAGE': 'local',
        'MANAGER': 'image',
        'THUMBNAIL_SIZE': None,  # Do not generate thumbnails
    }

class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # :memory:

    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH_OPTIONS = dict(bcrypt={'rounds': 4})
    SECURITY__SEND_MAIL_TASK = None
    DEBUG_TB_INTERCEPT_REDIRECTS = False
