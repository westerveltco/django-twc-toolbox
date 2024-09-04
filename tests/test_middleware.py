from __future__ import annotations

from http import HTTPStatus

import pytest
from django.http import HttpResponse
from django.test import override_settings

from django_twc_toolbox.middleware import WwwRedirectMiddleware


@pytest.fixture(autouse=True)
def allowed_hosts():
    with override_settings(ALLOWED_HOSTS=[".example.com"]):
        yield


@pytest.fixture
def middleware():
    return WwwRedirectMiddleware(lambda request: HttpResponse())


def test_www_redirect(middleware, rf):
    request = rf.get("/some-path/", HTTP_HOST="www.example.com")

    response = middleware(request)

    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response["Location"] == "http://example.com/some-path/"


def test_www_redirect_different_port(middleware, rf):
    request = rf.get("/some-path/", HTTP_HOST="www.example.com:8080")

    response = middleware(request)

    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response["Location"] == "http://example.com:8080/some-path/"


def test_non_redirect(middleware, rf):
    request = rf.get("/", HTTP_HOST="example.com")

    response = middleware(request)

    assert isinstance(response, HttpResponse)
    assert response.status_code == 200


def test_non_redirect_different_port(middleware, rf):
    request = rf.get("/", HTTP_HOST="example.com:8080")

    response = middleware(request)

    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
