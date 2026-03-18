# Aesthetic Biometrics Engine

Biometric facial analysis API for aesthetic medicine. Extracts objective measurements from standardized photographs to support treatment planning with Botulinum toxin and dermal fillers.

## What it does

Analyzes facial images from three perspectives:

| View | Measurements |
|---|---|
| **Frontal (0°)** | Symmetry score, facial thirds proportions, lip ratio |
| **Profile (90°)** | Ricketts E-line, nasolabial angle, chin projection |
| **Oblique (45°)** | Ogee curve, midface volume assessment |

Returns structured JSON — designed as an **Agent-as-a-Service** for AI workflows.

## Quick Start

```bash
# Clone & setup
git clone https://github.com/JNassar77/aesthetic-biometrics-engine.git
cd aesthetic-biometrics-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run
uvicorn app.main:app --reload --port 8000

# Or with Docker
docker compose up --build
```

API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Usage

```bash
curl -X POST "http://localhost:8000/api/v1/analyze?view_angle=frontal" \
  -F "file=@patient_frontal.jpg"
```

## Tech Stack

FastAPI · MediaPipe FaceMesh · OpenCV · Supabase · n8n · Docker

## Project Structure

```
CLAUDE.md              ← Project context (AI sessions)
README.md              ← You are here
app/                   ← Application code
  api/routes.py        ← API endpoints
  core/                ← Analysis engines (pure logic)
  models/schemas.py    ← Pydantic models
  services/            ← Supabase, n8n integration
  utils/geometry.py    ← Math helpers
docs/                  ← Documentation
  TASKS.md             ← Roadmap & backlog
  FEATURES.md          ← Feature catalog
  CONTRACTS.md         ← API schemas & data contracts
  ARCHITECTURE.md      ← System design & math
  GRAPH.md             ← Mermaid diagrams
  REGISTRY.md          ← Master artifact index
  DOD.md               ← Definition of Done
  CONTRIBUTING.md      ← Dev guide & code standards
tests/                 ← Test suite
```

## Documentation

| Document | Purpose |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Project context, conventions, commands |
| [`docs/TASKS.md`](docs/TASKS.md) | Phased roadmap with progress tracking |
| [`docs/FEATURES.md`](docs/FEATURES.md) | Feature specs with clinical relevance |
| [`docs/CONTRACTS.md`](docs/CONTRACTS.md) | API contracts, DB schemas |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Design, math, security |
| [`docs/GRAPH.md`](docs/GRAPH.md) | Visual system diagrams (Mermaid) |
| [`docs/REGISTRY.md`](docs/REGISTRY.md) | Master index of all artifacts |
| [`docs/DOD.md`](docs/DOD.md) | Quality gates for features/releases |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Dev setup, standards, testing |

## License

Proprietary — Praxis Nassar
