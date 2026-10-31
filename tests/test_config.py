import asyncio

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.main import app


@pytest.mark.parametrize(
    "url", ["http://127.0.0.1:11434", "http://localhost:1234/", "http://[::1]:11434"]
)
def test_local_origins_are_allowed(url):
    assert Settings(ollama_base_url=url).ollama_base_url == url.rstrip("/")


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://example.com",
        "http://localhost/api",
        "http://user:pass@localhost",
        "http://localhost?x=1",
        "http://localhost:99999",
    ],
)
def test_nonlocal_or_malformed_origins_are_rejected(url):
    with pytest.raises(ValidationError):
        Settings(ollama_base_url=url)


@pytest.mark.parametrize(
    "fields",
    [
        {"ollama_timeout_seconds": 0},
        {"ollama_timeout_seconds": 121},
        {"ollama_num_predict": -1},
        {"ollama_num_predict": 4097},
        {"ollama_model": " "},
    ],
)
def test_settings_reject_unbounded_or_blank_values(fields):
    with pytest.raises(ValidationError):
        Settings(**fields)


def test_exported_settings_are_loaded_and_cached(monkeypatch):
    get_settings.cache_clear()
    try:
        monkeypatch.setenv("OLLAMA_MODEL", "installed-test-model")
        monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "15")
        monkeypatch.setenv("OLLAMA_NUM_PREDICT", "512")
        settings = get_settings()
        assert settings.ollama_model == "installed-test-model"
        assert settings.ollama_timeout_seconds == 15
        assert settings.ollama_num_predict == 512
        monkeypatch.setenv("OLLAMA_NUM_PREDICT", "99999")
        assert get_settings() is settings
    finally:
        get_settings.cache_clear()


def test_invalid_settings_fail_application_startup(monkeypatch):
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "-1")
    get_settings.cache_clear()

    async def start():
        async with app.router.lifespan_context(app):
            pytest.fail("Invalid configuration must prevent startup")

    try:
        with pytest.raises(ValidationError):
            asyncio.run(start())
    finally:
        get_settings.cache_clear()
