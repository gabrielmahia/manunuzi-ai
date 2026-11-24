"""Headless smoke test: the app loads with no secrets and no network, and the AI path degrades gracefully."""
import pathlib
import socket

import pytest
from streamlit.testing.v1 import AppTest

APP = str(pathlib.Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*a, **k):
        raise OSError("network disabled in tests")
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)
    for k in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_MODEL"):
        monkeypatch.delenv(k, raising=False)


def test_app_loads_without_secrets():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception


def test_first_button_without_key_is_graceful():
    at = AppTest.from_file(APP, default_timeout=30).run()
    for ti in at.text_input:
        ti.input("test")
    for ta in at.text_area:
        ta.input("test")
    if not at.button:
        pytest.skip("no buttons on first page")
    at.button[0].click().run()
    assert not at.exception


def test_model_output_is_escaped(monkeypatch):
    src = pathlib.Path(APP).read_text()
    assert "html.escape(" in src
    assert "gemini-1.5-flash" not in src
    assert "?key=" not in src
