# Definition of Done — Aesthetic Biometrics Engine

> Quality gates that must be satisfied before any work item is considered complete.
> Nothing gets merged into `main` unless it passes the applicable checklist.

---

## Feature — Definition of Done

A feature is done when ALL of the following are true:

### Code Quality
- [ ] Code follows naming conventions (see `CONTRIBUTING.md`)
- [ ] Type hints on all function signatures
- [ ] Core analyzers remain pure functions (no I/O, no side effects)
- [ ] No hardcoded values — configuration via `config.py` or constants
- [ ] No `# TODO` left in code without a matching entry in `TASKS.md`

### Testing
- [ ] Unit tests written and passing for all new/changed logic
- [ ] Edge cases tested (empty input, boundary values, error conditions)
- [ ] Integration test covers the full API endpoint flow if a route changed
- [ ] All existing tests still pass (`pytest tests/ -v`)

### Documentation
- [ ] `FEATURES.md` updated with feature entry (purpose, workflow, output, clinical relevance)
- [ ] `CONTRACTS.md` updated if any API schema changed
- [ ] `REGISTRY.md` updated if new modules, endpoints, env vars, or tables were added
- [ ] `TASKS.md` checkbox marked as complete
- [ ] `GRAPH.md` updated if data flow or module dependencies changed
- [ ] Code docstring on module and public functions

### Integration
- [ ] Supabase schema migrated if DB changes were needed
- [ ] n8n webhook payload verified if response shape changed
- [ ] `.env.example` updated if new env vars were introduced
- [ ] No breaking changes to existing API consumers (or version bumped)

### Review
- [ ] Code committed with descriptive message (`feat:`, `fix:`, etc.)
- [ ] PR description explains what and why
- [ ] No secrets in committed code

---

## Bug Fix — Definition of Done

- [ ] Root cause identified and documented in commit message
- [ ] Fix implemented with minimal scope (no unrelated changes)
- [ ] Regression test added that would have caught the bug
- [ ] All existing tests still pass
- [ ] `TASKS.md` updated if fix was tracked there

---

## Refactor — Definition of Done

- [ ] Behavior is identical before and after (no functional changes)
- [ ] All existing tests pass without modification
- [ ] If module boundaries changed: `REGISTRY.md` and `GRAPH.md` updated
- [ ] `ARCHITECTURE.md` updated if structural design changed

---

## Release — Definition of Done

- [ ] All features in the release pass their individual DoD
- [ ] Full test suite passes: `pytest tests/ -v`
- [ ] Docker image builds successfully: `docker build -t aesthetic-biometrics .`
- [ ] Health endpoint responds: `GET /api/v1/health → 200`
- [ ] Swagger docs load: `GET /docs → 200`
- [ ] Version bumped in `app/main.py`
- [ ] Git tag created: `vX.Y.Z`
- [ ] All documentation files are current:

| Document | Current? |
|---|---|
| `CLAUDE.md` | [ ] |
| `TASKS.md` | [ ] |
| `FEATURES.md` | [ ] |
| `CONTRACTS.md` | [ ] |
| `ARCHITECTURE.md` | [ ] |
| `GRAPH.md` | [ ] |
| `REGISTRY.md` | [ ] |
| `CONTRIBUTING.md` | [ ] |
| `DOD.md` | [ ] |

---

## Quick Reference: Which docs to update?

| Change Type | Update These |
|---|---|
| New feature | FEATURES, CONTRACTS, REGISTRY, TASKS, GRAPH (if new flow) |
| API change | CONTRACTS, FEATURES (affected), REGISTRY (if new endpoint) |
| New module | REGISTRY, GRAPH, CLAUDE.md (directory structure) |
| DB migration | CONTRACTS (table schema), REGISTRY (table entry) |
| New env var | REGISTRY, .env.example, CLAUDE.md (if important) |
| Bug fix | TASKS (if tracked) |
| Refactor | REGISTRY, GRAPH, ARCHITECTURE (if structural) |
| Release | All docs — see release checklist above |
