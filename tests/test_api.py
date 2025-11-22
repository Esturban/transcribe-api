import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from api import api as api_module


@pytest.fixture()
def client() -> TestClient:
    return TestClient(api_module.app)


def test_transcribe_returns_transcript(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.setattr(
        api_module,
        "process_file",
        lambda path, *args, **kwargs: "Hi there",
    )

    response = client.post(
        "/transcribe",
        files={"file": ("audio.wav", b"fake-bytes", "audio/wav")},
    )

    assert response.status_code == 200
    assert response.json() == {"transcript": "Hi there"}


def test_transcribe_rejects_unsupported_extension(client: TestClient) -> None:
    response = client.post(
        "/transcribe",
        files={"file": ("note.txt", b"text", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_runtime_success(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    captured: Dict[str, object] = {}

    def fake_call_ai(**kwargs):
        captured.update(kwargs)
        return "Styled response"

    monkeypatch.setattr(api_module, "call_ai", fake_call_ai)

    response = client.post(
        "/runtime",
        json={
            "runtime_id": "content",
            "transcript": "Here is the transcript.",
            "params": {
                "prompt_prefix": "Summarize crisply:",
                "prompt_suffix": "Return bullet points.",
                "temperature": 0.4,
                "clean_markdown": True,
                "title": "Custom Title",
            },
            "prompt_override": "Use a custom instruction.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_id"] == "content"
    assert payload["content"] == "Styled response"
    assert payload["applied_params"]["temperature"] == 0.4
    assert payload["applied_params"]["title"] == "Custom Title"
    assert payload["applied_params"]["prompt_override"] is True
    assert "Summarize crisply" in captured["user_text"]
    assert captured["default_instructions"] == "Use a custom instruction."
    assert captured["instructions_env_var"] is None
    assert captured["clean_markdown"] is True


def test_runtime_unknown_runtime(client: TestClient) -> None:
    response = client.post(
        "/runtime",
        json={
            "runtime_id": "not-real",
            "transcript": "data",
        },
    )

    assert response.status_code == 404
    assert "Unknown runtime_id" in response.json()["detail"]


def test_runtime_invalid_temperature(client: TestClient) -> None:
    response = client.post(
        "/runtime",
        json={
            "runtime_id": "tasks",
            "transcript": "task body",
            "params": {"temperature": "not-a-number"},
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "temperature must be a number."

