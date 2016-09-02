from .settings import *

INSTALLED_APPS += [
    'tests'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'testing.sqlite3'),
    }
}
