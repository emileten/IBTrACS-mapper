from fastapi import FastAPI

from app.api.storms import router as storms_router

app = FastAPI(
    title="IBTrACS API",
    description="API for querying International Best Track Archive for Climate Stewardship (IBTrACS) tropical cyclone data",
    version="0.1.0"
)

# Include routers
app.include_router(storms_router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "IBTrACS API is running"}
