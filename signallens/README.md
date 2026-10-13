# SignalLens

**Evidence-backed local disruption intelligence.**

SignalLens turns scattered community reports, photos, and live weather data into a clear view of local disruptions, with the evidence behind each one and an explicit verification status.

> **Prototype, not an official alert system.** SignalLens is an information-triage tool. It must not be used for emergency decisions. AI outputs are *predictions*, not verified facts. Weather is *context*, not proof that an incident happened.

---

## Why it exists

When heavy rain, waterlogging, road closures, fallen trees, or infrastructure damage happen, useful information is spread across weather apps, government notices, group chats, and informal reports. It is hard to tell what is being reported, how fresh it is, what supports it, and whether it has been verified.

SignalLens puts reports, zero-shot text classification, live weather context, and provenance in one place, and it never presents a model output as truth.

## What works in this version (end-to-end vertical slice)

1. **Submit** a short description and choose an area. The backend validates the input and creates a report with status `Unverified`.
2. **Classify** the text with `facebook/bart-large-mnli` through Hugging Face Inference Providers, on the server. The result is stored as a prediction with its model ID, label, score and status.
3. **Fetch weather** for the selected coordinates from Open-Meteo. The retrieval time is stored.
4. **Inspect the evidence panel**, which separates the AI prediction, weather context, provenance, and human review into distinct sections.
5. **Review** a report with an explicit action. Allowed transitions are enforced by the server.

Failures are shown and never hidden. If the model or weather call fails, the report still displays, the failure is labelled, and you can retry. If `HF_TOKEN` is not set, the app says so. It does not invent a label.

## What is deliberately not included yet

| Area | Status |
|---|---|
| Image upload and image classification (`openai/clip-vit-base-patch32`) | Deferred. The spec puts this at P1, and it needs a tested provider route. |
| Map view (Leaflet + OpenStreetMap) | Deferred (P1). |
| Authentication, reviewer accounts | Out of scope. Status changes are not authoritative reviews. |
| Official alert feeds, duplicate detection, multilingual classification | Future work (P2). |
| A combined "danger" or "risk" score | Intentionally absent. See [Evidence model](#evidence-model). |
| Geocoding | Deferred. Areas are chosen from a list with known coordinates. |

## Architecture

A **modular monolith**: one React frontend and one FastAPI backend, with clear layers.

```text
Browser (React + TypeScript + Vite)
   │  JSON over HTTPS. No secrets in the browser.
   ▼
FastAPI  ── api/routes ──► services ──► repositories (SQLite)
                              │
                              ├──► providers/huggingface.py  (zero-shot text, server-side HF_TOKEN)
                              └──► providers/open_meteo.py   (current weather)
```

- **`api/routes`** validates HTTP input and maps errors to status codes. It holds no business logic.
- **`services`** hold the workflow: `reports.py` (orchestration), `classification.py`, `weather.py`, `evidence.py` (transparent checks), `status.py` (review transitions), and `categories.py` (the taxonomy).
- **`providers`** are adapters behind small interfaces (`TextClassifier`, `WeatherProvider`). Swapping a model or weather source means writing one new adapter. Pure parsers live in `parsers.py`, so they can be tested without network access.
- **`repositories`** persist data with the standard-library `sqlite3` module. A PostgreSQL version can replace it later without touching the services.
- **`schemas`** are Pydantic v2 models, which act as the typed API contract. The frontend mirrors them in `src/types/report.ts`.

Full design notes are in [`docs/`](docs/).

### Repository layout

```text
signallens/
├── backend/
│   ├── app/
│   │   ├── main.py            # app factory, CORS, error mapping
│   │   ├── config.py          # environment-based settings
│   │   ├── api/routes/        # reports, weather, health
│   │   ├── services/          # workflow, classification, weather, evidence, status, categories
│   │   ├── providers/         # Hugging Face and Open-Meteo adapters, parsers, interfaces
│   │   ├── repositories/      # SQLite persistence
│   │   ├── schemas/           # Pydantic request and response models
│   │   └── seed.py            # clearly labelled sample reports (no fabricated predictions)
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # layout, reports, evidence, weather, common
│   │   ├── features/report-submission/
│   │   ├── api/client.ts      # typed fetch wrapper with timeouts and error messages
│   │   ├── lib/               # formatting, labels, transitions
│   │   └── types/report.ts
│   └── .env.example
├── docs/                      # PRD, technical design, tech-stack specification, problem statement
├── LICENSE
└── README.md
```

## Quick start

You need Python 3.11+ and Node.js 18+.

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then set HF_TOKEN (see Configuration)
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. The OpenAPI docs are at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dashboard starts with clearly labelled sample reports.

### 3. Tests

```bash
cd backend
pytest
```

Service tests use fake providers. No network access or API keys are needed. The HTTP tests in `tests/test_api.py` are skipped automatically unless FastAPI and httpx are installed.

## Configuration

All configuration comes from environment variables. The backend reads `backend/.env`. Never commit `.env`.

| Variable | Where | Purpose |
|---|---|---|
| `HF_TOKEN` | backend, **secret** | Hugging Face token for inference. Without it, classification reports "unavailable" and does not guess. |
| `HF_TEXT_MODEL` | backend | Zero-shot model. Default `facebook/bart-large-mnli`. |
| `HF_INFERENCE_BASE_URL` | backend | Inference route base URL. |
| `HF_IMAGE_MODEL` | backend | Reserved for the image increment. Not used yet. |
| `OPEN_METEO_BASE_URL` | backend | Forecast endpoint. Default `https://api.open-meteo.com/v1/forecast`. |
| `DATABASE_URL` | backend | `sqlite:///./signallens.db` for the MVP. |
| `CORS_ORIGINS` | backend | Comma-separated frontend origins. Set this to your real origin when you deploy. |
| `HTTP_TIMEOUT_SECONDS` | backend | Timeout for each external call. Default `10`. |
| `STALE_AFTER_HOURS` | backend | Reports older than this are marked stale. Default `6`. |
| `SEED_DEMO_DATA` | backend | Seed the labelled sample reports on an empty database. Default `true`. |
| `VITE_API_BASE_URL` | frontend | Public API address. Default `http://localhost:8000`. |

Rule: **never put a secret in a `VITE_` variable.** Anything prefixed `VITE_` is shipped to the browser.

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/reports` | List reports, newest first (summary view) |
| `POST` | `/api/reports` | Submit a report. Runs classification and weather in the same request. Returns `201`. |
| `GET` | `/api/reports/{id}` | Full report: predictions, weather snapshot, evidence |
| `POST` | `/api/reports/{id}/classify` | Run or retry classification. Each run is stored as a new prediction. |
| `POST` | `/api/reports/{id}/weather` | Retry or refresh the weather snapshot |
| `PATCH` | `/api/reports/{id}/status` | Change review status with an explicit action. Invalid transitions return `409`. |
| `GET` | `/api/weather?latitude=&longitude=` | Live current conditions (not stored). Returns `503` when the provider fails. |

Errors: `404` for an unknown report, `409` for an invalid status change, `422` for invalid input, `503` for upstream weather failure. Model failures are not HTTP errors. They appear inside the report as an `unavailable` or `error` prediction, so the report still loads.

## Evidence model

The evidence panel shows **separate, labelled parts**:

1. **AI prediction**: predicted category, the model ID, and a **model score** (confidence in the label, not a probability that an incident happened).
2. **Weather context**: current conditions with observed and retrieved times. Labelled as context only.
3. **Provenance**: source type, source reference, submission and update times, coordinates, and report age.
4. **Checks**: each one is listed with its own result and detail:
   - `freshness`: recent or stale, based on `STALE_AFTER_HOURS`.
   - `source`: community, official, or sample data.
   - `model_agreement`: one model only, or disagreement between models.
   - `weather_context`: whether current rain is consistent with a rain-related category. Never proof.
   - `cross_modal`: image vs text. Not assessed until image classification is added.
5. **Human review**: current status, with explicit actions to change it.

There is **no combined score**. Scores are not added together into a risk or probability, because the inputs are not calibrated and there is no labelled dataset to validate them against. A high model score never changes a report's status.

## Review statuses

`unverified` → `under_review` / `confirmed` / `disputed`
`under_review` → `unverified` / `confirmed` / `disputed`
`confirmed` → `under_review` / `disputed` / `resolved`
`disputed` → `under_review` / `confirmed` / `resolved`
`resolved` → `under_review`

Every new report starts as `unverified`. The rules are enforced by `backend/app/services/status.py` and mirrored in `frontend/src/lib/status.ts` for display only.

## Limitations (please read)

- **Not an emergency system.** Do not use it for safety decisions, routing, or emergency response.
- **Model accuracy is unmeasured.** The MVP has not been evaluated on a labelled test set. Do not quote accuracy figures until you have measured them.
- **Zero-shot classification is approximate.** Labels such as "severe weather" overlap in meaning, and text can be ambiguous, sarcastic, or in another language.
- **Provider availability varies.** Confirm that your Hugging Face route serves the chosen model and task before relying on it. The request format used here follows the zero-shot task on the `hf-inference` route, and it should be checked against the provider's current docs.
- **Weather is a current snapshot.** It is not historical and it does not show what the road looked like at the time of the report.
- **Coverage is limited.** Only the areas in the selector are supported, with no geocoding and no official feeds.
- **Uploads are not implemented.** No user photos are accepted, so no image is ever analysed.
- **No moderation or abuse controls yet.** Do not open public submission before adding rate limiting, moderation, and abuse reporting.
- **Reviewer actions are unauthenticated.** Anyone who can reach the API can change a status. This is acceptable only for a local demo.
- **SQLite is single-instance.** Use PostgreSQL for multi-user deployment.

## Security and privacy

- Secrets live in environment variables on the server. The frontend never receives `HF_TOKEN`.
- Inputs are validated for length, coordinate range, and blank values. Unknown request fields are rejected.
- All external calls have timeouts, and transient failures get one bounded retry.
- CORS is restricted to configured origins.
- Submitters are not asked for names, phone numbers, or exact addresses. The form warns against including personal details.
- Upstream error messages are shown to users, but tokens are never echoed back.

## Roadmap

1. Measure classification quality on a small hand-labelled set (accuracy, per-class precision and recall). Publish the numbers with the sample size.
2. Add image classification behind a provider adapter. Show it as a separate prediction, with cross-modal agreement as a check.
3. Add a map view (Leaflet + OpenStreetMap) and filters for category, status, and recency.
4. Add PostgreSQL, migrations, and object storage for uploads.
5. Add authentication and reviewer roles, plus a review audit trail.
6. Add official alert feed adapters, with source-specific provenance.
7. Add duplicate-report detection and moderation tooling.
8. Add CI (GitHub Actions) for linting, type checking, and tests.

## Contributing

Good first contributions: a second text-classification adapter, a labelled evaluation set, multilingual labels, or an accessibility audit. Please keep the core principle: **predictions are labelled as predictions, and nothing is presented as verified without a human review step.**

## License

MIT. See [LICENSE](LICENSE).
