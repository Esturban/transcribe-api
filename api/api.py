import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from aims.assistants.utils import call_ai
from aims.utils import process_file

app = FastAPI(title="Transcribe API", version="0.1.0")

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv"}


def _is_supported_extension(suffix: str) -> bool:
    return suffix in ALLOWED_AUDIO_EXTENSIONS or suffix in ALLOWED_VIDEO_EXTENSIONS


async def _persist_upload(upload: UploadFile, *, chunk_size: int = 1024 * 1024) -> str:
    suffix = Path(upload.filename or "").suffix or ".tmp"
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            while True:
                chunk = await upload.read(chunk_size)
                if not chunk:
                    break
                tmp_file.write(chunk)
        return temp_path
    except Exception:
        os.remove(temp_path)
        raise


def _cleanup_paths(paths: Iterable[str]) -> None:
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except OSError:
            # Soft-fail cleanup; the main operation already succeeded/failed upstream.
            pass


@dataclass
class RuntimeDefinition:
    instructions_env_var: str
    default_instructions: str
    title: str
    temperature_env_var: Optional[str]
    default_temperature: float
    clean_markdown: bool = False

    def execute(
        self,
        transcript: str,
        params: Optional[Dict[str, Any]],
        prompt_override: Optional[str],
    ):
        params = params or {}
        applied_params: Dict[str, Any] = {}

        temperature_value = params.get("temperature")
        if temperature_value is None:
            env_value = os.getenv(self.temperature_env_var) if self.temperature_env_var else None
            try:
                temperature = float(env_value) if env_value is not None else float(self.default_temperature)
            except (TypeError, ValueError):
                temperature = float(self.default_temperature)
        else:
            try:
                temperature = float(temperature_value)
            except (TypeError, ValueError) as exc:
                raise ValueError("temperature must be a number.") from exc
        applied_params["temperature"] = temperature

        clean_markdown = bool(params.get("clean_markdown", self.clean_markdown))
        applied_params["clean_markdown"] = clean_markdown

        title = params.get("title", self.title)
        applied_params["title"] = title

        model = params.get("model")
        if model:
            applied_params["model"] = model

        prompt_prefix = params.get("prompt_prefix")
        prompt_suffix = params.get("prompt_suffix")

        user_text = transcript
        if prompt_prefix:
            user_text = f"{prompt_prefix}\n\n{user_text}"
            applied_params["prompt_prefix"] = prompt_prefix
        if prompt_suffix:
            user_text = f"{user_text}\n\n{prompt_suffix}"
            applied_params["prompt_suffix"] = prompt_suffix

        instructions_env_var = self.instructions_env_var
        default_instructions = self.default_instructions
        if prompt_override:
            instructions_env_var = None
            default_instructions = prompt_override

        response = call_ai(
            user_text=user_text,
            instructions_env_var=instructions_env_var,
            default_instructions=default_instructions,
            title=title,
            temperature=temperature,
            model=model,
            clean_markdown=clean_markdown,
        )

        if prompt_override:
            applied_params["prompt_override"] = True

        return response, applied_params


class RuntimeRequest(BaseModel):
    runtime_id: str = Field(..., description="Which runtime configuration to apply.")
    transcript: str = Field(..., description="Transcript text to feed into the runtime.", min_length=1)
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional runtime tweaks such as temperature, title, or prompt_prefix.",
    )
    prompt_override: Optional[str] = Field(
        default=None,
        description="Override the default system instructions for this runtime.",
    )


RUNTIME_DEFINITIONS: Dict[str, RuntimeDefinition] = {
    "content": RuntimeDefinition(
        instructions_env_var="CONTENT_INSTRUCTIONS",
        default_instructions="You are a helpful content assistant.",
        title="Content Assistant",
        temperature_env_var="CONTENT_TEMP",
        default_temperature=0.7,
    ),
    "tasks": RuntimeDefinition(
        instructions_env_var="TASK_INSTRUCTIONS",
        default_instructions="You are a helpful task assistant.",
        title="Task Assistant",
        temperature_env_var=None,
        default_temperature=0.2,
        clean_markdown=True,
    ),
    "teaching": RuntimeDefinition(
        instructions_env_var="TEACHING_INSTRUCTIONS",
        default_instructions="Create a teaching plan based on the user instructions.",
        title="Teaching Assistant",
        temperature_env_var=None,
        default_temperature=0.2,
        clean_markdown=True,
    ),
    "diagrammer": RuntimeDefinition(
        instructions_env_var="DIAGRAM_INSTRUCTIONS",
        default_instructions="Create a diagram based on the text.",
        title="Diagram Assistant",
        temperature_env_var=None,
        default_temperature=0.2,
        clean_markdown=True,
    ),
}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if not suffix:
        raise HTTPException(status_code=400, detail="Uploaded file must include an extension.")
    if not _is_supported_extension(suffix):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}.")

    temp_path = await _persist_upload(file)
    try:
        transcript = await run_in_threadpool(
            process_file, temp_path, None, False, False
        )
        if not transcript:
            raise HTTPException(status_code=500, detail="Transcription failed.")
        return {"transcript": transcript.strip()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        _cleanup_paths([temp_path])


@app.post("/runtime")
async def run_runtime(request: RuntimeRequest):
    definition = RUNTIME_DEFINITIONS.get(request.runtime_id)
    if definition is None:
        available = ", ".join(sorted(RUNTIME_DEFINITIONS.keys()))
        raise HTTPException(
            status_code=404,
            detail=f"Unknown runtime_id '{request.runtime_id}'. Available options: {available}",
        )

    try:
        response, applied_params = await run_in_threadpool(
            definition.execute,
            request.transcript,
            request.params,
            request.prompt_override,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=502, detail=response["error"])

    return {
        "runtime_id": request.runtime_id,
        "content": response,
        "applied_params": applied_params,
    }
