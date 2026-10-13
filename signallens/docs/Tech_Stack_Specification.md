# SignalLens --- Technology Stack Specification

**Version:** 1.0\
**Date:** 13 October 2026\
**Scope:** One-hour MVP, aligned with the SignalLens PRD, technical
design document, and build prompt.

## 1. Stack decision

Build SignalLens as a **React + TypeScript frontend backed by a FastAPI
modular monolith**. Use Hugging Face Inference Providers for AI
inference, Open-Meteo for live weather context, and SQLite for MVP
persistence.

The MVP should demonstrate one complete path:

**Submit report → classify text → optionally classify an image → fetch
weather context → display an evidence panel.**

Do not add microservices, authentication, a complex map, or advanced
analytics before this path works.

## 2. Technology stack at a glance

  -----------------------------------------------------------------------------------------------
  Layer              Selected technology              MVP use               Reason
  ------------------ -------------------------------- --------------------- ---------------------
  Frontend framework React 18                         Dashboard, report     Component-based UI
                                                      feed, form, evidence  
                                                      panel                 

  Build tool         Vite                             Local development and Fast setup
                                                      production build      

  Language           TypeScript                       UI state, API         Catches common
                                                      responses, component  integration errors
                                                      props                 

  Styling            Tailwind CSS                     Responsive layout and Fast styling
                                                      visual design         

  Design system      Small custom component/token     Cards, buttons,       Consistent UI without
                     layer                            badges, drawers,      a large component
                                                      status colors         framework

  Motion             Framer Motion                    Report cards, drawer, Polished interactions
                                                      button                
                                                      micro-interactions    

  Icons              Lucide React                     Navigation, report    Consistent icon set
                                                      categories, status    
                                                      indicators            

  Notifications      React Hot Toast                  Success, failure,     Clear feedback for
                                                      retry feedback        actions

  Maps               Leaflet + OpenStreetMap          Optional location map Include only if time
                                                                            allows

  Backend framework  FastAPI                          REST API and service  Lightweight Python
                                                      orchestration         API

  Runtime            Python 3.11+                     Backend runtime       Matches the project
                                                                            specification

  Request/response   Pydantic v2                      Validate report       Typed API contracts
  validation                                          payloads and response 
                                                      schemas               

  HTTP client        httpx                            Open-Meteo and        Timeouts and HTTP
                                                      Hugging Face requests error handling

  Environment        python-dotenv                    Local environment     Keeps secrets outside
  configuration                                       variables             source code

  Database           SQLite                           Store reports and     Minimal setup for an
                                                      metadata              MVP

  Persistence option SQLAlchemy or Python `sqlite3`   Database access       Choose one; pure
                                                                            `sqlite3` is fastest,
                                                                            SQLAlchemy is easier
                                                                            to extend

  AI access          Hugging Face Inference Providers Server-side model     Avoid hosting large
                                                      calls                 models in the MVP

  Text AI model      `facebook/bart-large-mnli`       Zero-shot             Uses the required
                                                      disruption-category   text-classification
                                                      classification        workflow

  Image AI model     `openai/clip-vit-base-patch32`   Optional image/text   Adds a visual
                                                      category matching     evidence signal when
                                                                            a photo is provided

  Weather data       Open-Meteo Forecast API          Current/forecast      Live external data
                                                      context for selected  
                                                      coordinates           

  Testing            pytest + FastAPI TestClient      Backend service and   Verify API behavior
                                                      endpoint tests        

  Version control    Git + public GitHub repository   Source history and    Open-source portfolio
                                                      community             
                                                      contributions         

  Frontend hosting   Netlify or Vercel                Deploy the Vite build Straightforward
                                                                            static hosting

  Backend hosting    Python/FastAPI-compatible host   Run API and keep      Separate API runtime
                                                      tokens server-side    

  Image storage      Local temporary storage for      Handle optional photo Avoid infrastructure
                     development                      uploads               setup in the first
                                                                            hour
  -----------------------------------------------------------------------------------------------

**Provider caveat:** Model IDs do not guarantee current inference
availability. Verify that the chosen Hugging Face provider supports each
model and the required task before relying on it. If a provider is
unavailable, show an explicit error state; never fabricate a prediction.

## 3. Required versus optional for the one-hour MVP

### Required

-   React 18, Vite, TypeScript, Tailwind CSS.
-   FastAPI, Python 3.11+, Pydantic v2.
-   `httpx` for external APIs and `python-dotenv` for local
    configuration.
-   Hugging Face text classification using `facebook/bart-large-mnli`,
    subject to provider availability.
-   Open-Meteo live weather lookup.
-   Report submission and an evidence panel.
-   Sample reports so the dashboard is not empty.
-   Explicit `Unverified / Needs Review` status.
-   Input validation, CORS configuration, upload size/type limits, and
    server-side credentials.

### Optional if time allows

-   Image classification using `openai/clip-vit-base-patch32`.
-   SQLite persistence if the report flow works first.
-   Leaflet map.
-   Framer Motion enhancements beyond the evidence drawer.
-   Automated frontend tests.
-   PostgreSQL, authentication, public alert ingestion, notifications,
    and background jobs are **not** part of the one-hour MVP.

If the image model integration is not available within the time budget,
keep the photo upload UI clearly marked as unavailable or defer it. Do
not label an image as AI-analyzed unless an actual model response was
received.

## 4. Frontend packages

Recommended initial dependencies:

``` bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install framer-motion lucide-react react-hot-toast
npm install leaflet
npm install -D tailwindcss @tailwindcss/vite
```

Follow the current Tailwind CSS Vite setup instructions for the
generated project version. If the map is not implemented, omit Leaflet
to save time.

### Frontend feature organization

``` text
frontend/src/
├── components/
│   ├── layout/
│   ├── reports/
│   ├── evidence/
│   └── weather/
├── features/
│   └── report-submission/
├── api/
│   └── client.ts
├── types/
│   └── report.ts
├── App.tsx
└── main.tsx
```

### UI design decisions

-   Soft dark theme with deep indigo surfaces and cyan/amber accents.
-   Glass-like cards used sparingly so text remains readable.
-   Responsive layout with report feed and selected-report evidence
    drawer.
-   Visible confidence/score bars labeled as **model scores**, not
    incident probabilities.
-   Distinct status styles for `Verified`, `Unverified`, and `Stale`.
-   Loading skeletons, useful empty states, retry actions, and readable
    error messages.
-   Persistent header note: **"Prototype --- not an official alert
    system."**

## 5. Backend packages

Recommended initial dependencies:

``` bash
pip install fastapi uvicorn httpx python-dotenv python-multipart
```

For SQLite persistence, choose one approach:

``` bash
# Option A: ORM
pip install sqlalchemy

# Option B: Python sqlite3
# No additional package required
```

For testing:

``` bash
pip install pytest
```

### Backend feature organization

``` text
backend/app/
├── main.py
├── config.py
├── api/
│   └── routes/
│       ├── reports.py
│       ├── weather.py
│       └── health.py
├── schemas/
│   ├── report.py
│   └── prediction.py
├── services/
│   ├── classification.py
│   ├── weather.py
│   ├── evidence.py
│   └── reports.py
├── repositories/
└── models/
```

Keep it a **modular monolith**: one FastAPI process, with routes,
service logic, and data access separated by responsibility. Avoid
microservices for this scope.

## 6. External integrations

### Hugging Face Inference Providers

Use the backend to make inference requests. The frontend must never
receive the Hugging Face secret token.

Text classification labels can start with: - flooding / waterlogging -
road closure - severe weather - fallen tree / infrastructure damage -
traffic disruption - unrelated / unclear

Treat zero-shot output as a model prediction. Store the model
identifier, label, score if returned, inference status, and timestamp.

For image classification, compare the uploaded image against a
controlled list of candidate labels. Store the returned labels and
scores if supported by the selected provider. Do not assume the score is
a calibrated probability of an incident.

### Open-Meteo

Use the selected location's latitude and longitude to retrieve current
or forecast weather context. Show the query location and retrieval time.
Weather is contextual evidence only; it does not establish that a road
is flooded or closed.

### Optional geocoding

For the fastest build, allow a manually selected city/area and use known
demo coordinates. Add geocoding later rather than making it a blocker
for the MVP.

## 7. Environment configuration

Example `backend/.env.example`:

``` dotenv
APP_ENV=development
CORS_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///./signallens.db
HF_TOKEN=
HF_TEXT_MODEL=facebook/bart-large-mnli
HF_IMAGE_MODEL=openai/clip-vit-base-patch32
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
```

Example `frontend/.env.example`:

``` dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Important: - Never commit `.env`. - Never place `HF_TOKEN` in a variable
prefixed with `VITE_`; frontend variables are exposed to browser code. -
Use host-managed environment variables for deployment. - Configure CORS
to the actual frontend origin in deployment rather than allowing every
origin.

## 8. Minimum API surface

  -------------------------------------------------------------------------------------------
  Method                  Endpoint                                    Purpose
  ----------------------- ------------------------------------------- -----------------------
  `GET`                   `/health`                                   Confirm the backend is
                                                                      running

  `GET`                   `/api/reports`                              List seeded or stored
                                                                      reports

  `POST`                  `/api/reports`                              Submit report text,
                                                                      location, and optional
                                                                      photo

  `GET`                   `/api/reports/{id}`                         Return report and
                                                                      evidence details

  `POST`                  `/api/reports/{id}/classify`                Run or retry model
                                                                      inference

  `GET`                   `/api/weather?latitude=...&longitude=...`   Fetch weather context

  `PATCH`                 `/api/reports/{id}/status`                  Change review status
                                                                      through an explicit
                                                                      action
  -------------------------------------------------------------------------------------------

For the one-hour version, submission and classification may be combined
into one endpoint. Keep response fields stable and report failures
explicitly.

## 9. Data and evidence contract

Each report should carry, when available:

-   Report ID and original description.
-   Location label and coordinates.
-   Source type/reference.
-   Creation timestamp.
-   Human review status.
-   Text model ID, predicted label, score if returned, and inference
    status.
-   Image model ID and prediction, if a real image inference was
    performed.
-   Weather provider, retrieval timestamp, and normalized weather
    summary.

Suggested status values:

`unverified`, `under_review`, `confirmed`, `disputed`, `resolved`.

A report starts as `unverified`. A high model score must not
automatically change it to `confirmed`.

## 10. Security and reliability baseline

-   Enforce maximum upload size and allow only supported image formats.
-   Validate both MIME type and file extension; generate safe
    server-side filenames.
-   Set timeouts on model and weather requests.
-   Handle upstream failures without crashing the dashboard.
-   Keep the original report view available when inference is
    unavailable.
-   Do not silently substitute sample predictions for failed live model
    calls.
-   Minimize personal data and do not expose submitter identity by
    default.
-   Restrict CORS to known origins.
-   Use explicit loading, failure, and retry states.
-   State clearly that the prototype is not an official alert or
    emergency service.

## 11. Deployment choices

### MVP

-   **Frontend:** Netlify or Vercel.
-   **Backend:** a host that supports Python/FastAPI.
-   **Database:** SQLite for a simple single-instance demo; confirm that
    the host's filesystem persists between deployments and restarts.
-   **Secrets:** host environment configuration.
-   **Uploads:** temporary/local development storage only unless
    persistent object storage is configured.

### Next iteration

-   PostgreSQL for multi-user persistence.
-   Object storage for uploaded images.
-   Database migrations.
-   Structured logs and request IDs.
-   Rate limiting and moderation.
-   CI via GitHub Actions.
-   Automated tests and model-quality evaluation.

Check current hosting limits, persistence behavior, free-tier
restrictions, and provider availability before deployment.

## 12. Build order

1.  Create the React layout with seeded report cards.
2.  Create FastAPI `/health` and report endpoints.
3.  Add Open-Meteo integration and display live retrieval time.
4.  Integrate real Hugging Face text classification.
5.  Connect submission to the evidence panel.
6.  Add image classification if supported and time permits.
7.  Add SQLite persistence and basic tests.
8.  Polish responsive behavior, error states, README, and deployment.

## 13. Definition of done

The MVP is complete when a user can submit a report, see a real
text-classification result, view live weather context, and inspect a
clear evidence panel. It must distinguish model predictions from
verification, handle provider failures honestly, protect secrets, and
run using documented setup instructions.

The portfolio story should emphasize end-to-end integration, typed API
contracts, external-service resilience, evidence provenance, and
responsible AI presentation---not simply the number of models used.
