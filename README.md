# Voice-Based Multilingual Minutes of Meeting (MoM) Generator

An end-to-end, privacy-focused Python application that converts multilingual meeting audio into structured, actionable Minutes of Meeting (MoM). The system handles audio preprocessing, speech-to-text transcription, speaker diarization, speaker analytics, and LLM-driven structured summarization, exporting professional reports in JSON, PDF, and DOCX formats.

## Key Features

- **Multilingual Speech-to-Text** — Converts audio into clean text using Whisper / IndicASR.
- **Speaker Diarization** — Identifies and separates individual speakers using PyAnnote diarization and embedding tracking.
- **Transcript-Diarization Alignment** — Synchronizes diarization timestamps with the transcript for accurate speaker attribution.
- **Speaker Analytics** — Computes talk-time, turn counts, and participation ratios per speaker.
- **Structured Summarization** — Generates Executive Summaries, Key Discussion Points, Decisions Made, and Action Items via LLM.
- **Document Export** — Auto-generates JSON, `.pdf`, and `.docx` reports.
- **REST API** — FastAPI-based service with upload, status polling, and export endpoints.
- **Streamlit UI** — Browser-based interface for uploading audio and viewing generated minutes.
- **Containerized Deployment** — Multi-stage Docker setup with CUDA/CPU support, optional Redis/Celery orchestration.

## Tech Stack & Architecture

### Core Components

| Pipeline Stage | Module | Description |
|---|---|---|
| Audio Processing | `core/audio_processor.py` | Audio conversion, chunking, FFmpeg extraction |
| Speaker Diarization | `core/diarization.py` | PyAnnote speaker diarization & embedding tracking |
| Transcription | `core/transcription.py` | Whisper / IndicASR multilingual speech-to-text |
| Alignment | `core/aligner.py` | Synchronizes diarization timestamps with transcript |
| Analytics | `core/analytics.py` | Speaker statistics — talk-time, turn counts, ratios |
| Summarization | `core/summarizer.py` | LLM-based MoM, Action Items, and Key Decision extraction |

### Backend & Infrastructure

- **REST API:** FastAPI
- **Web UI:** Streamlit (`app.py`)
- **Document Generation:** JSON, PDF, and DOCX exporter (`utils/exporter.py`)
- **Validation:** File format and corrupted media validation (`utils/validation.py`)
- **Logging:** Structured logging (`utils/logger.py`)
- **Configuration:** Environment variables, model configs, and path constants (`config/settings.py`)
- **Deployment:** Docker (multi-stage, CUDA/CPU support) with optional Redis/Celery for task orchestration

## Repository Structure

```
mom-pipeline/
│
├── config/
│   ├── __init__.py
│   └── settings.py              # Environment variables, model configs, path constants
│
├── core/
│   ├── __init__.py
│   ├── audio_processor.py       # Audio conversion, chunking, FFmpeg extraction
│   ├── diarization.py           # PyAnnote speaker diarization & embedding tracking
│   ├── transcription.py         # Whisper / IndicASR multilingual speech-to-text
│   ├── aligner.py               # Synchronizes diarization timestamps with speakers
│   ├── analytics.py             # Speaker statistics (talk-time, turn counts, ratios)
│   └── summarizer.py            # LLM-based MoM, Action Items, and Key Decision extractor
│
├── api/
│   ├── __init__.py
│   ├── app.py                   # FastAPI application initialization & middleware
│   ├── routes.py                # Upload, status polling, and export endpoints
│   └── schemas.py               # Pydantic data models for request/response validation
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Structured logging configuration
│   ├── exporter.py              # JSON, PDF, and DOCX report exporter
│   └── validation.py            # File format and corrupted media validation
│
├── storage/
│   ├── uploads/                 # Temporary storage for incoming audio/video files
│   └── outputs/                 # Generated transcripts, JSONs, and exported documents
│
├── tests/
│   ├── test_audio_processor.py
│   ├── test_diarization.py
│   └── test_pipeline.py
│
├── app.py                       # Streamlit web UI entry point
├── Dockerfile                   # Multi-stage Docker setup with CUDA/CPU support
├── docker-compose.yml           # Service orchestration (FastAPI + Redis/Celery optional)
├── requirements.txt             # Python dependency definitions
└── main.py                      # CLI & service entry point
```

## Getting Started

### Prerequisites

- **Python:** 3.10 to 3.13
- **FFmpeg** installed and available on your system PATH (used for audio extraction/conversion)
- **Docker** (optional, for containerized deployment)
- Any required API keys or model weights for your chosen Whisper / IndicASR and PyAnnote configuration — see `.env.example`

### Installation & Setup

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/mom-pipeline.git
cd mom-pipeline
```

**2. Create and Activate a Python Virtual Environment**

Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configure Environment Variables**

Create a `.env` file in the root project directory with the model configs and any required API keys, as defined in `config/settings.py`.

## Running the Application

The pipeline can be accessed in three ways — pick whichever fits your workflow.

### Option 1: CLI

If you want to run the pipeline directly from the command line:

```bash
python python main.py sample_meeting.mp3
```

### Option 2: Streamlit Web UI

If you want a browser-based interface for uploading audio and viewing the generated minutes:

```bash
streamlit run app.py
```

This launches a local web app (by default at `http://localhost:8501`) where you can upload a meeting recording and download the generated MoM once processing completes.

### Option 3: FastAPI REST API

If you want to access the pipeline as an API endpoint (for integration with other services):

```bash
uvicorn api.app:app --reload --port 8000
```

Access the interactive OpenAPI documentation at `http://localhost:8000/docs`.

### Option 4: Docker

Build and run the full stack (API, and optionally Redis/Celery for background processing):

```bash
docker-compose up --build
```

## Pipeline Execution Workflow

```
[ Upload Audio / Video ]
           │
           ▼
[ Audio Preprocessor (FFmpeg) ] ──► (Convert & Chunk Audio)
           │
           ├──► [ PyAnnote Diarization ] ──► (Speaker Timestamps & Embeddings)
           │
           └──► [ Whisper / IndicASR ] ──► (Multilingual Transcription)
                                              │
                                              ▼
                                 [ Aligner: Merge Transcript & Speakers ]
                                              │
                                              ▼
                                 [ Analytics: Talk-Time, Turns, Ratios ]
                                              │
                                              ▼
                                 [ LLM Summarizer ]
                                              │
                                              ▼
                                 [ Exporter: JSON / PDF / DOCX ]
```

1. **Preprocessing** — Input audio/video files are converted and chunked using FFmpeg.
2. **Diarization** — Audio is processed by PyAnnote to identify individual speakers and track embeddings across segments.
3. **Transcription** — Audio is processed through Whisper or IndicASR to extract text across supported languages.
4. **Alignment** — Diarization timestamps are synchronized with the transcript for accurate speaker attribution.
5. **Analytics** — Speaker-level statistics (talk-time, turn counts, participation ratios) are computed.
6. **Summarization** — The aligned, analyzed dialogue is fed into an LLM to extract structured meeting sections — Executive Summary, Key Discussion Points, Decisions, and Action Items.
7. **Export** — Results are rendered into JSON, PDF, and Word documents.

## Testing

Run the test suite with:

```bash
pytest tests/
```

Covers audio processing, diarization, and full pipeline integration tests.

## License

Distributed under the MIT License. See `LICENSE` for more information.
