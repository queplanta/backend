from django.db import models
from django.utils.translation import ugettext as _

from .choices import PRIVACY_CHOICES, PRIVACY_DEFAULT


class PrivacyField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['verbose_name'] = _("Privacidade")
        kwargs['choices'] = PRIVACY_CHOICES
        kwargs['default'] = PRIVACY_DEFAULT
        super(PrivacyField, self).__init__(*args, **kwargs)
