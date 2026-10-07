import json
import shutil
import uuid
import zipfile
from pathlib import Path

import geopandas as gpd

from app.config import UPLOAD_DIR
from app.services.crs_service import choose_projected_crs

FILES: dict[str, dict] = {}


def _safe_extract(zip_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            target = (destination / member.filename).resolve()
            if not str(target).startswith(str(destination)):
                raise ValueError("Unsafe ZIP file path detected.")
        zf.extractall(destination)


def _load_geodata(file_path: Path, work_dir: Path) -> gpd.GeoDataFrame:
    if file_path.suffix.lower() == ".kml":
        return gpd.read_file(file_path, driver="KML")

    _safe_extract(file_path, work_dir)
    shp_files = list(work_dir.rglob("*.shp"))
    if not shp_files:
        raise ValueError("ZIP does not contain a Shapefile (.shp).")
    return gpd.read_file(shp_files[0])


def process_upload(filename: str, data: bytes) -> dict:
    file_id = uuid.uuid4().hex
    file_dir = UPLOAD_DIR / file_id
    file_dir.mkdir(parents=True, exist_ok=True)
    source = file_dir / filename
    source.write_bytes(data)

    try:
        work_dir = file_dir / "work"
        work_dir.mkdir()
        gdf = _load_geodata(source, work_dir)

        crs_text = gdf.crs.to_string() if gdf.crs else None
        features = []
        projected_crs = None

        if gdf.crs:
            try:
                projected_crs = choose_projected_crs(gdf)
            except Exception:
                projected_crs = None

        projected = None
        if projected_crs is not None:
            projected = gdf.to_crs(projected_crs)

        for idx, row in gdf.iterrows():
            geom = row.geometry
            props = {
                str(k): (v.item() if hasattr(v, "item") else v)
                for k, v in row.drop(labels=["geometry"]).to_dict().items()
            }

            result = {
                "feature_id": int(idx) if isinstance(idx, (int,)) else len(features),
                "geometry_type": geom.geom_type if geom is not None else "None",
                "crs": crs_text,
                "geometry": geom.__geo_interface__ if geom is not None else None,
                "properties": props,
                "measurement": None,
                "measurement_status": "NOT_SUPPORTED",
            }

            if geom is None or geom.is_empty:
                result["measurement_status"] = "EMPTY_GEOMETRY"
            elif projected is None:
                result["measurement_status"] = "CRS_REQUIRED"
            else:
                pgeom = projected.loc[idx].geometry
                if geom.geom_type == "Polygon":
                    result["measurement"] = {
                        "area": float(pgeom.area),
                        "unit": "m²",
                    }
                    result["measurement_status"] = "COMPLETED"
                elif geom.geom_type == "MultiPolygon":
                    result["measurement"] = {
                        "area": float(pgeom.area),
                        "unit": "m²",
                    }
                    result["measurement_status"] = "COMPLETED"
                elif geom.geom_type == "LineString":
                    result["measurement"] = {
                        "length": float(pgeom.length),
                        "unit": "m",
                    }
                    result["measurement_status"] = "COMPLETED"
                elif geom.geom_type == "MultiLineString":
                    result["measurement"] = {
                        "length": float(pgeom.length),
                        "unit": "m",
                    }
                    result["measurement_status"] = "COMPLETED"
                elif geom.geom_type == "Point":
                    result["measurement_status"] = "NO_MEASUREMENT_REQUIRED"

            features.append(result)

        FILES[file_id] = {
            "id": file_id,
            "filename": filename,
            "feature_count": len(features),
            "crs": crs_text,
            "status": "COMPLETED",
            "features": features,
        }
        return FILES[file_id]
    except Exception:
        FILES[file_id] = {
            "id": file_id,
            "filename": filename,
            "feature_count": 0,
            "crs": None,
            "status": "FAILED",
            "features": [],
        }
        raise


def get_file(file_id: str) -> dict | None:
    return FILES.get(file_id)
