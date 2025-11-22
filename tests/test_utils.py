import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aims import utils as utils_module  # noqa: E402


def test_process_file_preserves_audio_extension(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake-audio")
    output_dir = tmp_path / "output"

    captured = {}

    def fake_convert(audio_path, verbose, write_files=True):
        captured["path"] = audio_path
        captured["verbose"] = verbose
        captured["write_files"] = write_files
        return "transcript"

    monkeypatch.setattr(utils_module, "convert_audio_to_text", fake_convert)

    result = utils_module.process_file(
        str(audio_file),
        output_audio_dir=str(output_dir),
        verbose=True,
        write_files=False,
    )

    assert result == "transcript"
    assert captured["path"] == str(audio_file)
    assert captured["verbose"] is True
    assert captured["write_files"] is False

    preserved_audio = output_dir / "sample.wav"
    assert preserved_audio.exists()
    assert not (output_dir / "sample.mp3").exists()
    assert not audio_file.exists()

