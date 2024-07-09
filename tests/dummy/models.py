from __future__ import annotations

from django.db import models

from django_twc_toolbox.models import WithHistory


class DateOrderableModel(models.Model):
    date = models.DateField()


class DateTimeOrderableModel(models.Model):
    date = models.DateTimeField()


class ModelWithHistory(WithHistory):
    name = models.CharField(max_length=255)


class Parent(models.Model):
    foo = models.CharField(max_length=255)


class Child(models.Model):
    parent = models.ForeignKey(
        "dummy.Parent", on_delete=models.CASCADE, related_name="parents"
    )
    bar = models.CharField(max_length=255)
