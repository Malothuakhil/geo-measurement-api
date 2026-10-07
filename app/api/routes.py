from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from app.models.schemas import FileInfo, MeasurementsResponse
from app.services.file_service import get_file, process_upload

router = APIRouter(prefix="/api/files", tags=["Files"])


@router.post("/", response_model=FileInfo, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only .kml or .zip files are supported.")

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(413, "File exceeds the 50 MB upload limit.")

    try:
        result = process_upload(filename, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(422, f"Unable to process geospatial file: {exc}")

    return result


@router.get("/{file_id}/", response_model=FileInfo)
def file_information(file_id: str):
    result = get_file(file_id)
    if not result:
        raise HTTPException(404, "File not found.")
    return result


@router.get("/{file_id}/measurements/", response_model=MeasurementsResponse)
def measurements(file_id: str):
    result = get_file(file_id)
    if not result:
        raise HTTPException(404, "File not found.")

    return {
        "file_id": result["id"],
        "filename": result["filename"],
        "feature_count": result["feature_count"],
        "crs": result["crs"],
        "measurements": result["features"],
    }
