from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core import checks
from django.contrib.auth.apps import AuthConfig as DjangoAuthConfig

from django.contrib.auth.management import create_permissions
from .auth_checks import check_user_model


class AccountsConfig(AppConfig):
    name = 'accounts'


class AuthConfig(DjangoAuthConfig):
    def ready(self):
        post_migrate.connect(
            create_permissions,
            dispatch_uid="django.contrib.auth.management.create_permissions")
        checks.register(check_user_model, checks.Tags.models)
