from __future__ import annotations

import sys

import pytest
from django.apps import apps

from django_twc_toolbox.tests import setup_test_app


@pytest.fixture(autouse=True, scope="function")
def dummy_app(tmp_path):
    app_dir = tmp_path / "dummy"
    app_dir.mkdir()

    init_py = app_dir / "__init__.py"
    init_py.write_text(
        """
from django_twc_toolbox.tests import setup_test_app

setup_test_app(__package__)
"""
    )

    models_py = app_dir / "models.py"
    models_py.write_text(
        """
from django.db import models

class DummyModel(models.Model):
    name = models.CharField(max_length=100)
"""
    )

    sys.path.insert(0, str(tmp_path))
    yield
    sys.path.pop(0)


def test_setup_test_app_valid_package():
    print(apps.app_configs)
    setup_test_app("dummy")
    assert "dummy_tests" in apps.app_configs


# @pytest.fixture(autouse=True, scope="function")
# def clean_app_registry():
#     original_app_configs = apps.app_configs.copy()
#     yield
#     apps.app_configs = original_app_configs
#     apps.clear_cache()
#
#
# def test_setup_test_app_valid_package():
#     package = "tests.dummy"
#     setup_test_app(package)
#     assert "dummy_tests" in apps.app_configs
#
#
# def test_setup_test_app_invalid_package():
#     with pytest.raises(ModuleNotFoundError):
#         setup_test_app("invalid_package")
#
#
# def test_setup_test_app_duplicate_label():
#     package = "tests.dummy"
#     setup_test_app(package)
#     with pytest.raises(ValueError):
#         setup_test_app(package)
#
#
# @pytest.mark.django_db
# def test_database_interaction():
#     package = "tests.dummy"
#     setup_test_app(package)
#     from .dummy.models import DummyModel
#
#     DummyModel.objects.create(name="Test")
#     assert DummyModel.objects.count() == 1
#     assert DummyModel.objects.first().name == "Test"
#
#
# @pytest.mark.django_db
# def test_no_setup_database_interaction():
#     try:
#         from .dummy.models import DummyModel  # noqa: F401
#
#         DummyModel.objects.count()
#         exists = True
#     except RuntimeError:
#         # The model should not be available if setup_test_app is not called
#         exists = False
#
#     assert not exists, "Model should not exist without setup_test_app"
