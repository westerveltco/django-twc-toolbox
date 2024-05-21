from __future__ import annotations

from django.db import models

from django_twc_toolbox.models import WithHistory


class DateOrderableModel(models.Model):
    date = models.DateField()


class DateTimeOrderableModel(models.Model):
    date = models.DateTimeField()


class ModelWithHistory(WithHistory):
    name = models.CharField(max_length=255)
