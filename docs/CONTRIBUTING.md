# Contributing — Aesthetic Biometrics Engine

## Development Setup

### Prerequisites
- Python 3.11+
- Docker Desktop (optional, for containerized dev)
- Git

### Local Setup

```bash
# Clone
git clone https://github.com/JNassar77/aesthetic-biometrics-engine.git
cd aesthetic-biometrics-engine

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run
uvicorn app.main:app --reload --port 8000

# Open API docs
# http://localhost:8000/docs
```

### Docker Setup

```bash
docker compose up --build
# API available at http://localhost:8000
```

## Branch Strategy

```
main ← stable, deployable
  └── feature/<name> ← new features
  └── fix/<name>     ← bug fixes
  └── refactor/<name> ← structural changes
```

- Branch from `main`
- Use descriptive branch names: `feature/auto-view-detection`, `fix/symmetry-edge-case`
- PR into `main` with description
- Squash merge preferred

## Code Standards

### Structure Rules
- **Core analyzers are pure functions**: input `FaceLandmarks`, output Pydantic model, no side effects
- **Services handle I/O**: database, HTTP, file system
- **Models define contracts**: all API input/output goes through Pydantic
- **Utils are stateless helpers**: math, conversion, no domain logic

### Style
- Type hints on all function signatures
- Docstrings on modules and public functions
- No `# TODO` without a matching TASKS.md entry
- Keep functions under 40 lines; extract if longer

### Naming
| Element | Convention | Example |
|---|---|---|
| Files | snake_case | `frontal_analyzer.py` |
| Classes | PascalCase | `FaceLandmarks` |
| Functions | snake_case | `analyze_frontal()` |
| Constants | UPPER_SNAKE | `LANDMARKS` |
| Env vars | UPPER_SNAKE | `SUPABASE_URL` |
| API routes | /kebab-case | `/api/v1/analyze` |
| DB tables | snake_case | `biometric_analyses` |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/test_frontal_analyzer.py -v

# With coverage
pytest tests/ --cov=app --cov-report=term-missing
```

### Test Organization
```
tests/
├── test_geometry.py           # Unit: geometry utils
├── test_frontal_analyzer.py   # Unit: frontal measurements
├── test_profile_analyzer.py   # Unit: profile measurements
├── test_oblique_analyzer.py   # Unit: oblique measurements
├── test_image_validator.py    # Unit: quality checks
├── test_api.py                # Integration: full endpoint
└── fixtures/                  # Test images
    ├── frontal_good.jpg
    ├── profile_good.jpg
    └── oblique_good.jpg
```

### Test Principles
- Mock external services (Supabase, n8n), never mock core analyzers
- Use real images for integration tests (store in `tests/fixtures/`)
- Assert numerical outputs within tolerance (`pytest.approx`)
- Every bug fix gets a regression test

## Commit Messages

```
<type>: <short description>

<optional body>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`

Examples:
```
feat: add nasolabial angle calculation to profile analyzer
fix: handle zero-division in lip ratio when mouth closed
docs: add Mermaid ER diagram to GRAPH.md
test: add edge case tests for symmetry with tilted face
```

## Key Files to Know

| File | Purpose | When to read |
|---|---|---|
| `CLAUDE.md` (root) | Project context for AI assistants | Start of every session |
| `docs/TASKS.md` | Roadmap and current work | Before starting new work |
| `docs/FEATURES.md` | Feature catalog with workflows | When implementing features |
| `docs/CONTRACTS.md` | API schemas and data contracts | When changing interfaces |
| `docs/GRAPH.md` | Visual system architecture | When understanding data flow |
| `docs/ARCHITECTURE.md` | Technical design and math | When modifying analysis logic |
| `docs/REGISTRY.md` | Master index of all artifacts | When looking for anything |
| `docs/DOD.md` | Quality gates | Before marking work as done |
