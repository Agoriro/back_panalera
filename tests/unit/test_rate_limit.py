from starlette.requests import Request

from src.interfaces.api.v1.routers.auth import get_rate_limit_key


def test_rate_limit_ignores_untrusted_forwarded_header() -> None:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"x-forwarded-for", b"198.51.100.20")],
            "client": ("203.0.113.10", 1234),
            "server": ("test", 80),
            "scheme": "http",
            "query_string": b"",
        }
    )

    assert get_rate_limit_key(request) == "203.0.113.10"
