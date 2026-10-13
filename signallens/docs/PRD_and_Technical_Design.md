# SignalLens --- Product Requirements Document, Technical Design & Technology Stack

**Document version:** 1.0\
**Date:** 13 October 2026\
**Status:** MVP specification\
**Product type:** Open-source, AI-assisted local disruption intelligence
prototype

------------------------------------------------------------------------

# 1. Product Requirements Document (PRD)

## 1.1 Product summary

**SignalLens** helps people review potential local disruptions---such as
waterlogging, severe weather, road closures, fallen trees, and
infrastructure damage---by bringing together user-submitted reports,
AI-assisted text/image classification, weather context, and traceable
evidence.

The MVP is an information-triage tool, not an official emergency-alert
system. It must clearly distinguish model predictions from independently
verified facts.

## 1.2 Problem statement

Information about local disruptions can be fragmented across weather
services, public notices, and community reports. Users may struggle to
assess whether a report is relevant, current, and supported by evidence.

SignalLens provides one place to submit or review a report, inspect its
evidence, see relevant weather context, and understand what remains
unverified.

## 1.3 Target users

-   **Commuters and residents:** want to understand potential local
    disruptions before travelling.
-   **Campus or facilities coordinators:** need a simple way to triage
    reports affecting a site.
-   **Community contributors:** want to submit reports and help review
    existing ones.
-   **Open-source contributors:** want to add data sources, labels,
    models, tests, and localization.

## 1.4 Goals

1.  Let a user submit a short text report and optionally attach a photo.
2.  Classify report text into a configurable set of disruption
    categories.
3.  Optionally classify a submitted image using a vision-language model.
4.  retrieve weather context for a selected location from Open-Meteo.
5.  Show report freshness, source, model output, weather retrieval time,
    and verification status.
6.  Provide a usable, responsive dashboard with clear loading and error
    states.
7.  Keep the architecture modular so that models, data sources, and
    storage can be changed later.
8.  Publish an understandable, reproducible open-source repository.

## 1.5 Non-goals for the MVP

-   Replacing emergency services or official warning systems.
-   Automatically dispatching emergency response or making
    safety-critical decisions.
-   Claiming that weather conditions prove a reported incident happened.
-   Building a full live social-media crawler or scraping private
    platforms.
-   Providing guaranteed route safety or real-time road-closure
    coverage.
-   Training a new foundation model.
-   Building a distributed microservices platform.
-   Promising calibrated incident probabilities without a validated
    dataset.

## 1.6 MVP scope and priority

### P0 --- Required

-   Responsive dashboard with a seeded example feed.
-   Report submission with description and manually selected location.
-   Text classification through a Hugging Face-supported inference
    route, where available.
-   Open-Meteo lookup for a selected location.
-   Incident detail panel with evidence and provenance fields.
-   Explicit statuses: `unverified`, `under_review`, `confirmed`,
    `disputed`, `resolved`.
-   API and model errors handled without crashing the interface.
-   `.env.example`; secrets excluded from Git.
-   README with setup, limitations, architecture, and license.

### P1 --- Include if time allows

-   Optional image upload and image classification.
-   SQLite persistence for reports and model outputs.
-   Category, status, and recency filters.
-   Report review action.
-   Basic automated tests.
-   Map view using Leaflet and OpenStreetMap tiles.

### P2 --- Future

-   PostgreSQL deployment.
-   Official public alert feeds and additional regional data sources.
-   Duplicate-report detection.
-   Cross-modal disagreement flags.
-   Multilingual classification.
-   Contributor reputation and audit trail.
-   Model evaluation dashboard and version comparisons.
-   Notifications and configurable saved areas.

## 1.7 User stories and acceptance criteria

### Story A --- Submit a report

As a resident, I want to submit a short report with a location so that
it can be categorized and reviewed.

**Acceptance criteria** - Description and location are required. - Input
length and uploaded file size/type are validated. - Successful
submission returns a report ID and timestamp. - The initial verification
status is `unverified`. - A failed request shows a useful error and
allows retry.

### Story B --- Classify report text

As a reviewer, I want to see a predicted category so that I can triage a
report faster.

**Acceptance criteria** - The API returns the predicted label and
available model score. - The interface labels this as an AI prediction,
not a verified fact. - Model/provider failures are visible and do not
prevent viewing the original report. - The model identifier is recorded
with the result.

### Story C --- View weather context

As a user, I want to see weather information for the report area to
understand the surrounding conditions.

**Acceptance criteria** - Weather is retrieved from Open-Meteo using a
selected or geocoded location. - The UI shows the location and retrieval
time. - Forecast/context is visually separated from incident evidence. -
API failures produce a retryable state. - Weather context is never
presented as proof that an incident occurred.

### Story D --- Inspect evidence

As a reviewer, I want to inspect a report's source, timestamp, model
outputs, and review status.

**Acceptance criteria** - Every report displays the information that is
available and clearly marks missing fields. - Model output, source
information, weather context, and human review are distinct. - Status
changes are reflected in the UI. - The application does not mark a
report confirmed solely because a model score is high.

### Story E --- Review a report

As a reviewer, I want to mark a report as confirmed, disputed, or
resolved.

**Acceptance criteria** - Status changes use explicit user action. - The
UI records the status and update time. - The MVP does not imply identity
verification or authoritative review unless such a process exists.

## 1.8 Main user flow

1.  User opens the dashboard.
2.  User chooses a location or opens a seeded report.
3.  User submits a description and optionally a photo.
4.  Backend validates and normalizes the submission.
5.  Text classifier runs; image classifier runs if an image is supplied
    and that feature is enabled.
6.  Backend retrieves weather context for the selected coordinates.
7.  Backend saves or returns the report and evidence bundle.
8.  Dashboard displays the category prediction, weather context,
    timestamps, and verification state.
9.  A human reviewer may update the report status.

## 1.9 Product success metrics

For a one-hour prototype, measure completion and reliability rather than
claiming societal impact.

-   **Happy-path completion:** a user can submit and view one report.
-   **API success rate:** successful requests divided by valid test
    requests.
-   **Latency:** record median and p95 response times separately for
    weather and model calls.
-   **Classification quality:** evaluate on a small, manually labeled
    test set; report accuracy and per-class precision/recall where
    sample size permits.
-   **Error recovery:** user can retry after a provider or network
    failure.
-   **Evidence completeness:** percentage of displayed reports showing
    source, timestamp, model ID, and status where applicable.
-   **Usability:** a first-time tester can submit and interpret a report
    without verbal assistance.

Do not claim a target such as "95% accurate" until measured on a
suitable test set.

## 1.10 Risks and mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  Model misclassification             Display model output as a
                                      prediction; enable human review

  Stale or fabricated community       Show timestamps and source; keep
  reports                             unverified status by default

  Weather mistaken for incident proof Present weather as context, never
                                      as confirmation

  Inference provider unavailable or   Handle errors, allow retry, and
  rate-limited                        keep seeded sample reports
                                      available

  API token leakage                   Store credentials server-side in
                                      environment variables

  Malicious image upload              Validate MIME type, extension, and
                                      size; avoid executing uploaded
                                      content

  Privacy concerns                    Collect minimal personal data;
                                      avoid exposing submitter details
                                      publicly

  Incomplete regional data            Clearly state data-source coverage
                                      and freshness

  Unlicensed model or data            Check the terms for each model and
                                      data source before redistribution
                                      or commercial use
  -----------------------------------------------------------------------

## 1.11 MVP release definition

The MVP is ready to demonstrate when a user can submit a report, receive
at least one real AI classification result, retrieve real weather
context, and inspect an evidence panel that distinguishes predictions
from verification. If inference is unavailable, the UI must say so
rather than fabricate an AI result.

------------------------------------------------------------------------

# 2. Technical Design Document

## 2.1 System overview

Build a **modular monolith**: one React frontend and one FastAPI backend
with clearly separated modules. This is simpler to implement and deploy
than microservices while preserving useful boundaries.

### Logical architecture

``` text
Browser
  |
  v
React + Vite frontend
  |
  | HTTPS / JSON / multipart upload
  v
FastAPI application
  |
  +--> Report service ----------> SQLite (MVP) / PostgreSQL (later)
  |
  +--> Classification service --> Hugging Face Inference Provider
  |          |
  |          +--> Text classification
  |          +--> Optional image classification
  |
  +--> Weather service ---------> Open-Meteo API
  |
  +--> Evidence/triage service -> freshness, provenance, disagreement flags
  |
  v
Normalized response to frontend
```

## 2.2 Proposed repository layout

``` text
signallens/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── reports/
│   │   │   ├── weather/
│   │   │   └── evidence/
│   │   ├── api/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── classification.py
│   │   │   ├── weather.py
│   │   │   ├── evidence.py
│   │   │   └── reports.py
│   │   ├── repositories/
│   │   └── models/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── PRD.md
│   └── DESIGN.md
├── .gitignore
├── LICENSE
└── README.md
```

For a strict one-hour build, this structure can be reduced. Keep at
least the API routes and external-service logic separate.

## 2.3 Main components

### Frontend

Responsibilities: - Report feed and report detail. - Submission form and
optional photo preview. - Weather context card. - Prediction labels and
evidence provenance. - Loading, empty, and error states. - Filters for
category, status, and recency if time allows.

The frontend must not call Hugging Face using a secret token. All
private credentials remain on the backend.

### Report API

Responsibilities: - Validate text, location, and file metadata. - Assign
server-generated IDs and timestamps. - Create reports with `unverified`
status. - Return normalized report objects. - Support listing and
retrieving reports. - Accept explicit review-status changes.

### Classification service

Responsibilities: - Call the configured inference provider. - Keep model
names and provider configuration in environment/configuration rather
than hard-coding them throughout the application. - Normalize provider
output into a stable internal schema. - Record model ID, predicted
label, score if available, and inference time. - Return a typed
unavailable/error result when inference fails.

Recommended initial text model: `facebook/bart-large-mnli` for zero-shot
classification, if supported by the selected inference provider.
Recommended optional image model: `openai/clip-vit-base-patch32`, if a
compatible provider supports it. Verify current provider availability
and request/response formats before implementation.

### Weather service

Responsibilities: - Accept latitude and longitude. - Request relevant
current or forecast values from Open-Meteo. - Apply a timeout and handle
HTTP errors. - Normalize response fields. - Record the retrieval
timestamp and location. - Avoid treating a forecast as a historical
observation or incident confirmation.

For the fastest MVP, allow the user to select a city and use known demo
coordinates. Add geocoding as a separate feature rather than making it a
hard dependency.

### Evidence and triage service

Responsibilities: - Calculate report age from its timestamp. - Track
provenance and whether each field is known or missing. - Compare text
and image categories when both are available. - Flag disagreements for
human review. - Produce transparent indicators such as `recent`,
`stale`, `model_disagreement`, and `source_unverified`.

Do not call these indicators a calibrated "risk score." If a composite
score is added later, document its formula and validate it against
labeled data.

### Persistence

For the first working version: - Use SQLite or in-memory seeded data if
necessary. - Store report metadata, model predictions, and review
status. - Store uploaded files locally only for a local demo; do not
assume local disk is durable in a deployed environment.

For deployment: - Move to PostgreSQL. - Use object storage for images. -
Store file metadata and object references in the database. - Define
retention and deletion rules.

## 2.4 Data model

### Report

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `id`                    UUID/string             Server-generated
                                                  identifier

  `description`           string                  User-provided report

  `category`              string/null             Predicted category, not
                                                  ground truth

  `latitude`              decimal/null            Selected coordinates

  `longitude`             decimal/null            Selected coordinates

  `location_label`        string                  Human-readable location

  `source_type`           enum/string             `community`,
                                                  `official`, `demo`

  `source_reference`      string/null             URL or reference when
                                                  available

  `created_at`            datetime UTC            Submission time

  `status`                enum                    `unverified`,
                                                  `under_review`,
                                                  `confirmed`,
                                                  `disputed`, `resolved`

  `image_reference`       string/null             Storage key or local
                                                  reference

  `updated_at`            datetime UTC            Last update
  -----------------------------------------------------------------------

### Prediction

  Field          Type           Notes
  -------------- -------------- -------------------------------------------------
  `id`           UUID/string    Prediction identifier
  `report_id`    UUID/string    Related report
  `task`         string         `text_classification` or `image_classification`
  `model_id`     string         Exact checkpoint/model identifier
  `label`        string         Predicted label
  `score`        decimal/null   Provider score if supplied
  `created_at`   datetime UTC   Inference time
  `status`       string         `success`, `unavailable`, `error`

### Weather snapshot

  Field                      Type           Notes
  -------------------------- -------------- ---------------------------------
  `id`                       UUID/string    Snapshot identifier
  `report_id`                UUID/string    Related report
  `provider`                 string         `open-meteo`
  `latitude` / `longitude`   decimal        Query coordinates
  `payload_summary`          JSON           Only relevant normalized values
  `retrieved_at`             datetime UTC   Retrieval time

For the one-hour MVP, these can be represented by simpler SQLAlchemy
models or Pydantic response objects. Avoid overengineering persistence
before the happy path works.

## 2.5 API design

Suggested endpoints:

  -------------------------------------------------------------------------------------------
  Method                  Endpoint                                    Purpose
  ----------------------- ------------------------------------------- -----------------------
  `GET`                   `/health`                                   Basic health check

  `GET`                   `/api/reports`                              List seeded or saved
                                                                      reports

  `POST`                  `/api/reports`                              Submit report;
                                                                      multipart if image is
                                                                      attached

  `GET`                   `/api/reports/{id}`                         Fetch report and
                                                                      evidence

  `POST`                  `/api/reports/{id}/classify`                Trigger or retry
                                                                      classification

  `GET`                   `/api/weather?latitude=...&longitude=...`   Retrieve weather
                                                                      context

  `PATCH`                 `/api/reports/{id}/status`                  Change review status
  -------------------------------------------------------------------------------------------

The MVP may combine report submission and classification into one
endpoint. Keep the response schema consistent so the frontend does not
depend on a specific inference provider.

Example normalized classification response:

``` json
{
  "task": "text_classification",
  "model_id": "facebook/bart-large-mnli",
  "label": "flooding",
  "score": 0.82,
  "status": "success",
  "is_verified": false
}
```

The score above is illustrative, not a real prediction. The API must
return the actual provider output or an explicit error state.

## 2.6 Error handling and resilience

-   Set timeouts for all external API calls.
-   Distinguish invalid user input (`400`/`422`), missing resources
    (`404`), rate limits (`429`), and upstream failures (`502`/`503`).
-   Do not fail the whole report view if weather or inference is
    unavailable.
-   Use a bounded retry strategy for transient errors; avoid unbounded
    retries.
-   Keep the original report accessible if model inference fails.
-   Return a request/correlation ID for debugging if time permits.
-   Never silently substitute a hard-coded prediction when a real model
    call fails.

## 2.7 Security and privacy

-   Keep tokens in environment variables and exclude `.env` from version
    control.
-   Validate file size, allowed image MIME types, and file extensions.
-   Generate safe server-side file names; never trust the original
    filename.
-   Avoid collecting phone numbers or precise submitter identity in the
    MVP.
-   Restrict CORS to known frontend origins in deployment.
-   Apply request-size limits and basic rate limiting before public
    launch.
-   Do not publish uploaded images without consent.
-   Document that submitted reports may be inaccurate.
-   Add moderation and abuse-reporting controls before opening public
    submissions broadly.

## 2.8 Testing strategy

### Unit tests

-   Category normalization.
-   Freshness calculation.
-   Status transition validation.
-   Provider response normalization.
-   Evidence/disagreement flags.

### API tests

-   Submit a valid report.
-   Reject empty descriptions and invalid coordinates.
-   Return `404` for unknown report IDs.
-   Handle unavailable model provider.
-   Handle unavailable weather provider.
-   Ensure new reports remain unverified by default.

### Manual acceptance test

1.  Start the frontend and backend.
2.  Submit a report with a valid description and location.
3.  Verify that a real model result is displayed, or a clear provider
    error is shown.
4.  Verify weather values come from an actual API response.
5.  Inspect source, timestamp, model ID, and verification status.
6.  Test network failure and retry.
7.  Confirm that no secrets appear in browser requests or Git history.

## 2.9 Deployment plan

**Prototype** - Frontend: Vercel or Netlify. - Backend: a host that
supports Python/FastAPI. - Database: SQLite only for a single-instance
demo, or managed PostgreSQL if persistence must survive deployments. -
Secrets: host environment settings.

**Production-oriented next stage** - Managed PostgreSQL. - Object
storage for uploads. - Structured logs and request IDs. - Health checks
and monitoring. - Database migrations. - Rate limits, moderation,
backups, and retention policy.

Check the selected hosting provider's current free-tier, filesystem
persistence, and sleep/usage restrictions before deployment.

## 2.10 Future scalability

1.  Introduce provider adapters so model vendors can be swapped.
2.  Add asynchronous inference jobs for slow models.
3.  Add PostgreSQL indexes for location, category, status, and creation
    time.
4.  Store images in object storage with retention policies.
5.  Add official data-source adapters with source-specific provenance.
6.  Add deduplication using time, location, and semantic similarity.
7.  Version the category taxonomy and evaluation dataset.
8.  Measure model quality and latency before changing default models.

------------------------------------------------------------------------

# 3. Technology Stack

## 3.1 Recommended MVP stack

  --------------------------------------------------------------------------------
  Layer                   Technology                       Reason
  ----------------------- -------------------------------- -----------------------
  Frontend                React + TypeScript + Vite        Fast development,
                                                           maintainable
                                                           components, typed API
                                                           contracts

  Styling                 Tailwind CSS                     Rapid responsive UI
                                                           development

  UI components           Accessible custom components or  Avoid spending the MVP
                          a lightweight component library  budget building every
                                                           control from scratch

  Backend                 Python + FastAPI                 Clear REST APIs,
                                                           validation, automatic
                                                           OpenAPI docs

  Validation              Pydantic                         Typed request and
                                                           response schemas

  AI inference            Hugging Face Inference Providers Avoid hosting large
                                                           models during the first
                                                           iteration

  Text model              `facebook/bart-large-mnli`       Zero-shot category
                                                           classification when
                                                           provider-supported

  Image model             `openai/clip-vit-base-patch32`   Optional zero-shot
                                                           image/text matching
                                                           when provider-supported

  Weather                 Open-Meteo API                   Live weather context
                                                           without requiring a
                                                           standard API key for
                                                           non-commercial use

  Database                SQLite initially; PostgreSQL for Low setup overhead now,
                          deployed multi-user use          stronger deployment
                                                           option later

  ORM                     SQLAlchemy, optional in the      Familiar persistence
                          first hour                       abstraction and future
                                                           database portability

  HTTP client             `httpx`                          Timeouts and
                                                           asynchronous requests
                                                           from FastAPI

  Maps                    Leaflet + OpenStreetMap          Optional location
                                                           visualization

  Testing                 pytest + FastAPI TestClient;     Regression protection
                          Vitest for frontend if time      
                          permits                          

  Version control         Git + public GitHub repository   Contribution workflow
                                                           and portfolio
                                                           visibility

  Frontend hosting        Netlify or Vercel                Straightforward static
                                                           frontend deployment

  Backend hosting         Python-compatible application    Runs FastAPI and keeps
                          host                             credentials server-side

  Image storage           Local files for development;     Avoid relying on
                          object storage later             ephemeral production
                                                           disk

  CI                      GitHub Actions, later            Automated linting and
                                                           tests
  --------------------------------------------------------------------------------

## 3.2 Environment variables

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

The exact Hugging Face provider and request format must be selected and
tested. Model IDs alone do not guarantee that an inference provider
currently serves a checkpoint.

Example `frontend/.env.example`:

``` dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Never put `HF_TOKEN` in a `VITE_` variable because frontend environment
variables are exposed to browser code.

## 3.3 Local development commands

### Backend

``` bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install fastapi uvicorn httpx python-dotenv python-multipart
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` to inspect the FastAPI OpenAPI
interface.

Add the Hugging Face client, SQLAlchemy, and test dependencies only when
needed.

### Frontend

``` bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install tailwindcss @tailwindcss/vite
npm run dev
```

Follow the current Tailwind CSS Vite setup instructions for the
generated Vite version.

## 3.4 Suggested implementation order

1.  Build the dashboard with seeded reports.
2.  Add FastAPI health and report endpoints.
3.  Connect Open-Meteo using selected coordinates.
4.  Add text inference through a tested provider.
5.  Display model ID, prediction, timestamp, and unverified status.
6.  Add optional image classification.
7.  Add persistence and tests.
8.  Deploy and document the project.

## 3.5 Definition of done

The project is demonstrably functional when:

-   The frontend and backend run locally from documented instructions.
-   At least one report can be submitted and displayed.
-   At least one AI task uses a real inference result.
-   Weather context is fetched from a live API.
-   Model outputs are clearly labeled as predictions.
-   Failures are surfaced honestly and do not break the dashboard.
-   Credentials are not committed or exposed to the frontend.
-   The repository contains a README, architecture description, setup
    steps, license, and limitations.

------------------------------------------------------------------------

# 4. Portfolio and GitHub presentation

## Recommended repository description

**SignalLens is an open-source, AI-assisted local disruption triage
prototype that combines report classification, optional image
understanding, live weather context, and evidence provenance.**

## Recommended demo sequence

1.  Open the dashboard and select a location.
2.  Submit a report such as "Water is collecting near the underpass."
3.  Show the actual text-classification response.
4.  Display live weather context and its retrieval time.
5.  Upload an optional sample photo and show image-model output if
    implemented.
6.  Explain why the report remains unverified until reviewed.
7.  Demonstrate graceful handling of a failed external API request.

Use clearly labeled sample data for any incident that is not a real,
verified event. Do not imply that an illustrative report represents a
live emergency.

## Suggested next GitHub issues

-   Add a second text-classification model and compare results.
-   Add multilingual report classification.
-   Add official public alert feed adapter.
-   Add duplicate-report detection.
-   Add a labeled evaluation dataset and model metrics.
-   Add review audit history.
-   Add accessibility checks and keyboard navigation.
-   Add deployment workflow and CI tests.

## Final recommendation

Build the narrow end-to-end workflow first: **report submission → real
text classification → live weather context → evidence panel**. Treat
image classification, maps, authentication, notifications, and advanced
analytics as later increments. A small, reliable, honest implementation
is a stronger portfolio artifact than a broad interface whose AI and
data integrations are simulated.
