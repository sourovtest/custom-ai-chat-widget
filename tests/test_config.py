from backend import config


def test_shared_ai_api_key_and_generic_brand_are_loaded(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setenv("AI_API_KEY", "test-provider-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("BRAND_NAME", "Example Store")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://shop.example, https://admin.example/")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    settings = config._load_settings()

    assert settings.gemini_api_key == "test-provider-key"
    assert settings.brand_name == "Example Store"
    assert settings.cors_allowed_origins == (
        "https://shop.example",
        "https://admin.example",
    )


def test_legacy_cors_setting_remains_supported(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://legacy.example")

    assert config._read_origins() == ("https://legacy.example",)
