# type: ignore
from __future__ import annotations

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError


class Command(createsuperuser.Command):
    help = "Create or update superuser."

    def handle(self, *args, **options):
        try:
            super().handle(*args, **options)
        except CommandError as err:
            if "That username is already taken" not in str(err) or not settings.DEBUG:
                raise err

            User = get_user_model()

            username = options[User.USERNAME_FIELD]
            user = User.objects.get(username=username)

            password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
            user.set_password(password)

            if email := options[User.EMAIL_FIELD]:
                user.email = email

            user.save()
