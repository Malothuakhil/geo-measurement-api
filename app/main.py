from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0",
    description="Upload KML/Shapefile data and obtain CRS-aware geometry measurements.",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
