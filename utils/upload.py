import uuid
import os

from django.utils import timezone
from django.utils.text import slugify


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


def set_upload_to_random_filename(folder):
    def set_upload_to(instance, filename):
        today = timezone.now()
        new_filename = random_file_name()
        filename = build_filename(filename, new_filename)
        path = os.path.join(folder, today.strftime("%Y/%m"))
        return os.path.join(path, filename)
    return set_upload_to


def set_upload_to_random_folder(folder):
    def set_upload_to(instance, filename):
        today = timezone.now()
        new_folder_name = random_file_name()
        path = os.path.join(folder, today.strftime("%Y/%m"), new_folder_name)
        filename = slugify_filename(filename)
        return os.path.join(path, filename)
    return set_upload_to
