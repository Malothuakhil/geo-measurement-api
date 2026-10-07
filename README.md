# Geospatial File Measurement API

A production-oriented FastAPI backend that accepts KML files or ZIP archives containing Shapefiles, extracts geospatial features, handles CRS transformation, and returns measurements.

## Features

- FastAPI REST API
- KML upload
- ZIP/Shapefile upload
- Polygon and MultiPolygon area calculation
- LineString and MultiLineString length calculation
- Point support with no measurement
- CRS-aware measurement calculations
- Automatic UTM projected CRS selection for geographic CRS
- ZIP path-traversal protection
- File-size validation
- Graceful handling of unsupported geometries
- Swagger/OpenAPI documentation
- Pytest tests
- Docker support

## Requirements

- Python 3.11+
- GDAL/GEOS/PROJ runtime libraries for local GeoPandas installation
- Docker (optional)

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Open Swagger:

http://127.0.0.1:8000/docs

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run with Docker

```bash
docker compose up --build
```

Swagger:

http://localhost:8000/docs

## API

### 1. Upload

`POST /api/files/`

Multipart form field:

`file`

Accepted:

- `.kml`
- `.zip` containing `.shp`, `.shx`, `.dbf` and preferably `.prj`

Example:

```bash
curl -X POST "http://localhost:8000/api/files/"   -F "file=@survey.kml"
```

Example response:

```json
{
  "id": "abc123",
  "filename": "survey.kml",
  "feature_count": 120,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

### 2. File information

`GET /api/files/{id}/`

Example:

```bash
curl "http://localhost:8000/api/files/abc123/"
```

### 3. Measurements

`GET /api/files/{id}/measurements/`

Example:

```bash
curl "http://localhost:8000/api/files/abc123/measurements/"
```

Example response:

```json
{
  "file_id": "abc123",
  "filename": "survey.kml",
  "feature_count": 2,
  "crs": "EPSG:4326",
  "measurements": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "crs": "EPSG:4326",
      "geometry": {},
      "properties": {
        "name": "Area A"
      },
      "measurement": {
        "area": 15432.67,
        "unit": "m²"
      },
      "measurement_status": "COMPLETED"
    },
    {
      "feature_id": 1,
      "geometry_type": "LineString",
      "crs": "EPSG:4326",
      "geometry": {},
      "properties": {
        "name": "Road A"
      },
      "measurement": {
        "length": 523.41,
        "unit": "m"
      },
      "measurement_status": "COMPLETED"
    }
  ]
}
```

## Architecture

```text
Client
  |
  v
FastAPI Router
  |
  v
File Validation
  |
  v
File Processing Service
  |
  +--> KML reader
  |
  +--> ZIP extraction -> Shapefile reader
  |
  v
GeoPandas GeoDataFrame
  |
  v
CRS Service
  |
  +--> Geographic CRS -> local UTM CRS
  |
  v
Measurement Service
  |
  +--> Polygon -> Area
  +--> LineString -> Length
  +--> Point -> No measurement
  +--> Unsupported -> Graceful status
  |
  v
JSON Response
```

## File-processing flow

1. Validate extension.
2. Read the upload into memory.
3. Enforce a 50 MB limit.
4. Create an isolated file directory.
5. For ZIP files, validate every archive member before extraction.
6. Locate the Shapefile.
7. Read the file using GeoPandas.
8. Extract CRS, geometry and properties.
9. Calculate measurements using a projected CRS.
10. Store the processed result for subsequent API requests.

## CRS handling

Area and distance should not be calculated directly from latitude/longitude coordinates because EPSG:4326 coordinates are angular degrees.

The service therefore:

1. Reads the source CRS.
2. Leaves already-projected datasets in their projected CRS.
3. For geographic datasets, calculates a representative centroid in WGS84.
4. Selects the corresponding UTM zone.
5. Reprojects the dataset to that UTM CRS.
6. Calculates area in square metres and length in metres.

This strategy works well for datasets covering a relatively local area. Very large or cross-zone datasets could use an equal-area or geodesic strategy in a future version.

## Measurement rules

| Geometry | Measurement |
|---|---|
| Polygon | Area |
| MultiPolygon | Area |
| LineString | Length |
| MultiLineString | Length |
| Point | None required |
| Other geometry | Graceful NOT_SUPPORTED response |

## Error handling

The API returns appropriate HTTP errors for:

- Unsupported extensions: `400`
- Invalid ZIP contents: `400`
- Missing Shapefile: `400`
- Files larger than 50 MB: `413`
- Missing file ID: `404`
- Processing failures: `422`

Individual unsupported geometries do not cause the entire file to fail.

## Testing

Run:

```bash
pytest -q
```

The test suite covers API health validation, invalid uploads, and projected CRS selection.

## Design decisions

### Why FastAPI?

FastAPI provides strong request validation, automatic OpenAPI documentation, asynchronous upload handling, and a small, maintainable application structure.

### Why GeoPandas?

GeoPandas provides a mature interface for reading geospatial vector data and integrates naturally with Shapely and PyProj.

### Why UTM?

UTM provides metre-based coordinates and is appropriate for many local/regional datasets. Selecting the zone from the feature centroid avoids hard-coding a CRS for all files.

### In-memory metadata store

For this assignment, processed file metadata is kept in an in-memory dictionary. This keeps the implementation simple while demonstrating the API and geospatial processing flow.

For production, this should be replaced by PostgreSQL/PostGIS or another persistent store.

## Learning

This project demonstrates:

- FastAPI REST API development
- Multipart file handling
- GeoPandas/Shapely processing
- CRS and coordinate-system concepts
- Projection-aware spatial measurement
- Secure ZIP extraction
- API validation and error handling
- Automated testing
- Docker-based deployment

## Future scope

- PostgreSQL/PostGIS persistence
- Background processing for large files
- Object storage such as S3
- Authentication and authorization
- Pagination for large feature collections
- Geodesic measurements for very large datasets
- Multiple projected CRS strategies
- Job/status APIs for asynchronous processing
- Rate limiting
- Structured logging and observability
- CI/CD with GitHub Actions
