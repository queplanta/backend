import uuid
import os

from django.utils import timezone
from django.utils.text import slugify
from django.utils.deconstruct import deconstructible


def random_file_name():
    return str(uuid.uuid4())


def build_filename(filename, new_filename):
    ext = filename.split('.')[-1]
    return "%s.%s" % (new_filename, ext)


def slugify_filename(filename):
    # remove ext
    new_filename = ".".join(filename.split('.')[0:-1])
    new_filename = slugify(new_filename)
    return build_filename(filename, new_filename)


@deconstructible
class set_upload_to_random_filename(object):
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        today = timezone.now()
        new_filename = random_file_name()
        filename = build_filename(filename, new_filename)
        path = os.path.join(self.folder, today.strftime("%Y/%m"))
        return os.path.join(path, filename)


@deconstructible
class set_upload_to_random_folder(object):
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        today = timezone.now()
        new_folder_name = random_file_name()
        path = os.path.join(self.folder, today.strftime("%Y/%m"), new_folder_name)
        filename = slugify_filename(filename)
        return os.path.join(path, filename)

