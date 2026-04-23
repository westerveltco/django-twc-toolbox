from __future__ import annotations

from unittest import mock

import httpx
import pytest

from django_twc_toolbox.decorators import req


def test_req(monkeypatch):
    monkeypatch.setattr("django.conf.settings.DEBUG", False)
    url = "https://example.com/test-hc"

    @req(url)
    def foo():
        pass

    with mock.patch.object(httpx, "get") as mock_httpx_get:
        foo()

        mock_httpx_get.assert_called_once_with(url, timeout=5)


@pytest.mark.parametrize("url", ["", "invalid"])
def test_req_invalid_url(url, caplog):
    with caplog.at_level("ERROR"):

        @req(url)
        def foo():
            pass

    assert "Invalid URL" in caplog.text
