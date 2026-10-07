from typing import Any
from pydantic import BaseModel


class FileInfo(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: str | None
    status: str


class Measurement(BaseModel):
    feature_id: int
    geometry_type: str
    crs: str | None
    geometry: dict[str, Any]
    properties: dict[str, Any]
    measurement: dict[str, Any] | None = None
    measurement_status: str


class MeasurementsResponse(BaseModel):
    file_id: str
    filename: str
    feature_count: int
    crs: str | None
    measurements: list[Measurement]
