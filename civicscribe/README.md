# CivicScribe

A universal conversational form-filling app with Form Packs.

## Stack
- Frontend: React (Vite), Tailwind
- Auth: Auth0 (Google + email/password)
- Backend: FastAPI (Python)
- LLM: Gemini (JSON mode)
- TTS: ElevenLabs
- DB/Storage: Supabase (Postgres + Storage)
- Doc Parsing: Google Document AI
- PDF Fill: PyPDF2 (AcroForm) + ReportLab overlay fallback

## Monorepo
```
civicscribe/
  apps/
    web/
    api/
  packs/
    snap/
    volunteer_waiver/
  infra/
```

## Setup
1) Supabase: create project, run `infra/supabase_schema.sql`.
2) Auth0: create app, set allowed callback `http://localhost:5173/welcome`, audience for API.
3) Google DocAI: set processor ID and credentials.
4) ElevenLabs: API key.
5) Gemini: API key.

Copy envs:
- `apps/api/.env.example` -> `.env`
- `apps/web/.env.example` -> `.env`

## Run
- Backend:
```
uvicorn apps.api.main:app --reload --port 8000
```
- Frontend:
```
cd apps/web && npm run dev
```

## Demo assets
- `packs/snap/form.pdf` (AcroForm fields)
- `packs/snap/sample_income_statement.pdf` (for upload)
- `packs/volunteer_waiver/form.pdf`

## Demo Script (Meet Maria)
1) Open `/`, click Start, sign in with Auth0.
2) On `/welcome`, click SNAP card.
3) Chat asks: "Hello! I can help you with your SNAP application. What is your full name?" and plays audio.
4) Provide answers for each field. Progress updates.
5) When asked for income, upload `sample_income_statement.pdf`. Bot confirms monthly income.
6) When complete, click Download Completed Form and verify 10+ fields populated.

Notes modal shows pack notes.
