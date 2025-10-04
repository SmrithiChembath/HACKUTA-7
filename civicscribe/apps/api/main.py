from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routers import health, packs, sessions, uploads, render

app = FastAPI(title="CivicScribe API", version="0.1.0")

# CORS for local dev; tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(packs.router, prefix="/packs", tags=["packs"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(uploads.router, prefix="/sessions", tags=["uploads"])  # nested under /sessions/{id}/upload
app.include_router(render.router, prefix="/sessions", tags=["render"])  # /sessions/{id}/render

@app.get("/health")
def health_root():
    return {"ok": True}
