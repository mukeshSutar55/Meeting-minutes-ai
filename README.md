# Voice-Based Multilingual Minutes of Meeting (MoM) Generator

An end-to-end, privacy-focused Python application that converts multilingual meeting audio (English, Hindi, Odia, Marathi) into structured, actionable Minutes of Meeting (MoM). The system handles audio preprocessing, speech-to-text transcription via Groq Whisper, speaker diarization via PyAnnote / Deepgram Nova-3, speaker-transcript alignment, speaker analytics, and LLM-driven structured summarization (Groq API), exporting professional reports in JSON, PDF, and DOCX formats.

## Key Features

- **Multilingual Speech-to-Text (Groq Whisper)** — Rapid, cost-effective transcription using `whisper-large-v3` with optimized prompt priming for code-switching across English, Hindi (हिंदी), Odia (ଓଡ଼ିଆ), and Marathi (मराठी).
- **Speaker Diarization (PyAnnote / Deepgram Nova-3)** — Identifies and separates individual speakers using PyAnnote or Deepgram Nova-3 speaker embedding tracking.
- **Transcript-Diarization Alignment (TranscriptAligner)** — Synchronizes diarization timestamps with transcript segments, using nearest-neighbor fallback for silence gaps and merging consecutive speaker turns.
- **Speaker Analytics** — Computes talk-time, turn counts, and participation ratios per speaker.
- **Structured Summarization (Groq LLM)** — Dynamic speaker identification (mapping Person 1 to real names), executive summaries, key discussion points, decisions made, and assigned action items via Groq API.
- **Document Export** — Auto-generates structured JSON, `.pdf`, and `.docx` reports.
- **REST API** — FastAPI service with upload, status polling, module-level execution (`/transcribe`, `/align`, `/summarize`), and export endpoints.
- **Streamlit UI** — Interactive browser UI for uploading recordings, visualizing speaker talk-time, and viewing/downloading generated minutes.
- **Containerized Deployment** — Multi-stage Docker setup with CUDA/CPU support, optional Redis/Celery task queue orchestration.

## Tech Stack & Architecture

### Core Components

| Pipeline Stage | Module | Key Library / API | Description |
|---|---|---|---|
| Audio Processing | `core/audio_processor.py` | FFmpeg, pydub, PyAV | Audio conversion, normalization (16kHz WAV), and chunking |
| Speaker Diarization | `core/diarization.py` | pyannote.audio / Deepgram API | Speaker segmentation and embedding tracking |
| Transcription | `core/transcription.py` | groq (whisper-large-v3) | Multilingual speech-to-text with segment timestamps |
| Alignment | `core/aligner.py` | Native Python | Overlap calculation, gap filling, and consecutive turn merging |
| Analytics | `core/analytics.py` | Native Python | Calculates talk-time, turn counts, and participation ratios |
| Summarization | `core/summarizer.py` | groq (llama-3.3-70b / mixtral-8x7b) | LLM-driven MoM generation with JSON mode & speaker name mapping |

### Backend & Infrastructure

- **Framework:** Python 3.10+
- **REST API:** FastAPI & Uvicorn
- **Web UI:** Streamlit (`app.py`)
- **LLM & Speech Engines:** Groq API (`whisper-large-v3`, Llama models)
- **Document Generation:** `reportlab` (PDF), `python-docx` (Word), `json`
- **Logging & Config:** Structured logging (`utils/logger.py`), Pydantic settings (`config/settings.py`)
- **Deployment:** Docker, docker-compose (with optional Redis/Celery)

## Repository Structure

```
mom-pipeline/
│
├── config/
│   ├── __init__.py
│   └── settings.py              # Environment variables, Groq/Deepgram API keys, model paths
│
├── core/
│   ├── __init__.py
│   ├── audio_processor.py       # Audio extraction, WAV conversion, and chunking via FFmpeg
│   ├── diarization.py           # Speaker diarization via PyAnnote or Deepgram Nova-3
│   ├── transcription.py         # Groq Whisper (whisper-large-v3) speech-to-text engine
│   ├── aligner.py               # Synchronizes diarization timestamps with transcript turns
│   ├── analytics.py             # Speaker statistics (talk-time, turn counts, ratios)
│   └── summarizer.py            # Groq LLM-based MoM, Action Items, & Speaker Name mapping
│
├── api/
│   ├── __init__.py
│   ├── app.py                   # FastAPI application initialization, CORS, & middleware
│   ├── routes.py                # Upload, process, async polling, and document export endpoints
│   └── schemas.py               # Pydantic request/response validation schemas
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Structured logging configuration
│   ├── exporter.py              # JSON, PDF, and DOCX document generators
│   └── validation.py            # Audio file format and integrity validation
│
├── storage/
│   ├── uploads/                 # Temporary storage for uploaded audio/video files
│   └── outputs/                 # Generated transcripts, MoM JSONs, PDF/DOCX exports
│
├── tests/
│   ├── test_audio_processor.py
│   ├── test_diarization.py
│   ├── test_transcription.py
│   └── test_pipeline.py
│
├── app.py                       # Streamlit web UI entry point
├── main.py                      # CLI runner & FastAPI service bootstrapper
├── Dockerfile                   # Multi-stage Docker setup with CUDA/CPU support
├── docker-compose.yml           # Multi-container orchestration (FastAPI + Redis/Celery)
├── requirements.txt             # Project dependencies
└── .env.example                 # Environment variables template
```

## Getting Started

### Prerequisites

- **Python:** 3.10 to 3.13
- **FFmpeg:** Installed and added to system PATH
- **Groq API Key:** Required for Groq Whisper transcription and MoM LLM generation
- **HuggingFace / PyAnnote Token:** (Optional) Required if running PyAnnote locally

### Installation & Setup

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/mom-pipeline.git
cd mom-pipeline
```

**2. Create and Activate Virtual Environment**

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

Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
```

`.env` contents:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_WHISPER_MODEL=whisper-large-v3
GROQ_LLM_MODEL=openai/gpt-oss-20b
DEEPGRAM_API_KEY=your_deepgram_key
```

## Running the Application

### Option 1: CLI Execution

Run the complete end-to-end pipeline on an audio/video file directly from the command line:

```bash
python main.py storage/uploads/sample_meeting.mp3
```

### Option 2: Streamlit Web Interface

Launch the interactive web UI to upload audio, view transcript timelines, inspect speaker analytics, and download PDF/DOCX reports:

```bash
streamlit run app.py
```

Access the UI at `http://localhost:8501`.

### Option 3: FastAPI REST API

Start the FastAPI backend with Uvicorn:

```bash
uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

Access interactive OpenAPI docs at `http://localhost:8000/docs`.

### Option 4: Docker & Docker Compose

Build and launch the full containerized stack:

```bash
docker-compose up --build
```

## Pipeline Execution Workflow

```
[ Upload Audio / Video File ]
            │
            ▼
[ Audio Preprocessor (FFmpeg) ] ──► (16kHz WAV Conversion & Chunking)
            │
            ├──► [ PyAnnote / Nova-3 Diarization ] ──► (Speaker Timestamps: Person 1, Person 2)
            │
            └──► [ Groq Whisper Transcription ] ──► (Multilingual Timed Text Segments)
                                                       │
                                                       ▼
                                            [ Transcript Aligning ]
                                (Time-overlap matching & consecutive speaker turn merging)
                                                       │
                                                       ▼
                                            [ Speaker Analytics ]
                                    (Talk-time %, turn counts, ratios)
                                                       │
                                                       ▼
                                            [ Groq LLM Summarizer ]
                            (Name mapping, Executive Summary, Decisions, Action Items)
                                                       │
                                                       ▼
                                            [ Exporter Service ]
                                      (Generates JSON, PDF, and DOCX)
```

1. **Preprocessing** — Input audio/video is normalized to standard mono 16kHz WAV via FFmpeg.
2. **Diarization** — Audio is segmented into speaker turns (Person 1, Person 2).
3. **Transcription** — Transcribed via Groq `whisper-large-v3` with multilingual prompt hints.
4. **Alignment** — `TranscriptAligner` maps timed text segments to speaker turns and merges consecutive utterances.
5. **Analytics** — Calculates participant talk-time percentages and interaction turn ratios.
6. **Summarization** — Groq LLM extracts real participant names, executive summaries, decisions made, and assigned action items into validated JSON.
7. **Export** — Generates `.json`, `.pdf`, and `.docx` reports in `storage/outputs/`.

## Testing

Run the test suite with pytest:

```bash
pytest tests/
```

## License

Distributed under the MIT License. See `LICENSE` for details.