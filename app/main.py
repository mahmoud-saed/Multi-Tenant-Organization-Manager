from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, organizations, items, audit_logs

app = FastAPI(title="Multi-Tenant Organization Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(items.router, tags=["Items"])
app.include_router(audit_logs.router, tags=["Audit Logs"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
