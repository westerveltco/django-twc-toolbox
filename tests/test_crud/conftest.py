from __future__ import annotations

import pytest
from django.test import override_settings


@pytest.fixture(autouse=True)
def crud_settings():
    with override_settings(ROOT_URLCONF="tests.test_crud.views"):
        yield
