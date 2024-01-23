from __future__ import annotations

from django.db import models

from django_twc_toolbox.models import TimeStamped


class TestModel(TimeStamped):
    test_field = models.CharField(max_length=255, default="test")
