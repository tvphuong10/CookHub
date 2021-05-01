import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / "db.sqlite3"),
    }
}
