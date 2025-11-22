# Transcriber  

> An API designed to transcribe and summarize meetings

## Overview  

The goal of this API is to offer transcriptions and the ability to pass transcripts to other functions in the API to use AI assistants.

### Note:
 
The API first began as an attempt to summarize meetings and create subtitles for videos. However, this API began to change when I realized I needed "workspace admin authorization" for specific files and API access with Zoom. So what this became was an improved transcription software where I can speak into a microphone and use a small model to convert my speech into text and pass that into another LLM to condense the thoughts on paper. So it serves3 functions:

- Parse audio from a video 
- Convert audio into text
- Summarize text using OpenRouter AI's free models

## Installation  

### Requirements  

The following are a few of the packages that are relied upon by this API:
```bash
torch==2.5.1
tiktoken==0.9.0
openai-whisper==20240930
moviepy==2.1.2
evernote3=1.25.14
oauth2==3.2.2
fastapi==0.103.1
```

### Steps to install  

#### For development  

1. Clone the repository
```bash
git clone https://github.com/Esturban/transcriber-api.git
cd transcriber-api
```

2. Install the required packages

```bash
pip install -r requirements.txt
```


#### For server  

To run the API, there's a couple of ways you can run the fastapi and test out the function:

3. Run the API

```bash

```

## Usage

### Run the API locally

```bash
uvicorn api.api:app --reload
```

### Docker

Build the image (runs the multi-stage build with cached wheels):

```bash
docker build -t transcribe-api .
```

Run the container and expose port 8000:

```bash
docker run --rm -p 8000:8000 --env-file .env transcribe-api
```

### Endpoints

#### `POST /transcribe`

- Body: multipart form-data with a single `file` upload (audio/video).
- Response: `{ "transcript": "<string>" }`.
- Uses the local Whisper Tiny pipeline via `aims.process_file` without writing intermediate artifacts.

Example:

```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@/path/to/audio.wav"
```

#### `POST /runtime`

- Body:
  ```json
  {
    "runtime_id": "content",
    "transcript": "string",
    "params": {
      "temperature": 0.4,
      "prompt_prefix": "Rewrite this for executives."
    },
    "prompt_override": "Optional custom system instructions."
  }
  ```
- `runtime_id` options: `content`, `tasks`, `teaching`, `diagrammer`.
- Response: `{ "runtime_id": "...", "content": "...", "applied_params": { ... } }`.
- Pass `prompt_override` to bypass the default system prompt or tweak behaviour with `params`.

## Documentation

## Tests

## Contributing

## License

## FAQ

**Why not use an Alpine base image?**  
Whisper, PyTorch, and ffmpeg rely on glibc-based binaries; musl-based Alpine images break those prebuilt wheels, forcing painful rebuilds (or outright failures). The slim Debian base keeps compatibility while staying lean.

**Is the current image the slimmest possible?**  
For this dependency stack, effectively yes. You could chase marginal savings with `debian:bookworm-slim` or distroless roots, but you'd still need the same heavyweight wheels. Going lighter would mean dropping features (e.g., no Whisper/ffmpeg) or accepting brittle builds.

**Any specialized bases worth considering?**  
If you need GPU acceleration, PyTorch's or NVIDIA's CUDA images are tuned for that, though they’re larger. For purely CPU FastAPI apps, `python:slim-bullseye` (what we use) or `tiangolo/uvicorn-gunicorn-fastapi:python3.12-slim` offer the best balance of size and ready-made tooling.

