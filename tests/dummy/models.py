from __future__ import annotations

from django.db import models


class DateOrderableModel(models.Model):
    date = models.DateField()


class DateTimeOrderableModel(models.Model):
    date = models.DateTimeField()
