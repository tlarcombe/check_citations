import pytest
from unittest.mock import patch, MagicMock


def test_live_url_returns_accessible():
    from scripts.check_url import check
    result = check("https://docs.python.org/3/")
    assert result["accessible"] is True
    assert result["status_code"] == 200
    assert "final_url" in result


def test_dead_url_returns_inaccessible():
    from scripts.check_url import check
    result = check("https://this-url-definitely-does-not-exist-abcxyz123.com/")
    assert result["accessible"] is False
    assert result["error"] is not None


def test_doi_url_follows_redirect():
    from scripts.check_url import check
    result = check("https://doi.org/10.1038/nature12373")
    assert "accessible" in result
    assert "final_url" in result


def test_result_schema():
    from scripts.check_url import check
    with patch("scripts.check_url.requests") as mock_req:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://example.com"
        mock_req.get.return_value = mock_resp
        result = check("https://example.com")
    assert set(result.keys()) >= {"accessible", "status_code", "final_url", "error"}


def test_timeout_returns_inaccessible():
    from scripts.check_url import check
    import requests as req_lib
    with patch("scripts.check_url.requests.get", side_effect=req_lib.Timeout):
        result = check("https://example.com")
    assert result["accessible"] is False
    assert "timeout" in result["error"].lower()
