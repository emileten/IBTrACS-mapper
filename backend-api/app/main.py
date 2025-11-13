from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.storms import router as storms_router
from app.core.config import settings

app = FastAPI(
    title="IBTrACS API",
    description="API for querying International Best Track Archive for Climate Stewardship (IBTrACS) tropical cyclone data",
    version="0.1.0"
)

cors_origins = settings.cors_origins
if cors_origins is not None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

# Include routers
app.include_router(storms_router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "IBTrACS API is running"}
