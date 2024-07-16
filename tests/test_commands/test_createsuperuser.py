from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.management import CommandError
from django.core.management import call_command
from django.test.utils import override_settings
from model_bakery import baker

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
def test_createsuperuser():
    user = baker.make("User", is_superuser=True)

    with patch.dict(os.environ, {"DJANGO_SUPERUSER_PASSWORD": "password"}):
        call_command("createsuperuser", interactive=False, username=user.username)

    user.refresh_from_db()

    assert user.check_password("password")


@override_settings(DEBUG=True)
def test_createsuperuser_update_email():
    user = baker.make("User", is_superuser=True, email="test@example.com")

    with patch.dict(os.environ, {"DJANGO_SUPERUSER_PASSWORD": "password"}):
        call_command(
            "createsuperuser",
            interactive=False,
            username=user.username,
            email="updated@example.com",
        )

    user.refresh_from_db()

    assert user.email == "updated@example.com"


@override_settings(DEBUG=False)
def test_createsuperuser_not_debug():
    user = baker.make("User", is_superuser=True)

    with patch.dict(os.environ, {"DJANGO_SUPERUSER_PASSWORD": "password"}):
        with pytest.raises(CommandError):
            call_command("createsuperuser", interactive=False, username=user.username)


@override_settings(
    INSTALLED_APPS=[
        app for app in settings.INSTALLED_APPS if app != "django_twc_toolbox"
    ]
)
def test_createsuperuser_no_toolbox():
    user = baker.make("User", is_superuser=True)

    with patch.dict(os.environ, {"DJANGO_SUPERUSER_PASSWORD": "password"}):
        with pytest.raises(CommandError):
            call_command("createsuperuser", interactive=False, username=user.username)
