from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional
from shapely.geometry import shape, Polygon
import uuid
import datetime as dt

app = FastAPI(
    title="Rio Grande Due Diligence Demo API",
    version="0.1.0",
    description="A small demo backend that simulates flood + wildfire risk scoring using geospatial logic."
)


# ----------------------------
# Pydantic Models
# ----------------------------

class GenerateReportRequest(BaseModel):
    geometry: Dict  # GeoJSON polygon
    project_name: Optional[str] = None


class PillarScore(BaseModel):
    name: str
    score: float
    details: Dict


class GenerateReportResponse(BaseModel):
    report_id: str
    created_at: str
    overall_risk_score: float
    pillars: List[PillarScore]
    pdf_url: str
    kmz_url: str


# ----------------------------
# Mock Geospatial Pillar Logic
# ----------------------------

def compute_flood_risk(geom: Polygon):
    """Simulates flood risk using a fixed box in New Mexico."""
    flood_zone = Polygon([
        (-106.5, 34.5),
        (-106.5, 36.5),
        (-104.5, 36.5),
        (-104.5, 34.5),
    ])

    inter_area = geom.intersection(flood_zone).area
    parcel_area = geom.area
    fraction = inter_area / parcel_area if parcel_area > 0 else 0

    score = fraction * 100

    details = {
        "intersection_area": inter_area,
        "parcel_area": parcel_area,
        "fraction_in_flood_zone": fraction,
    }

    return score, details


def compute_wildfire_risk(geom: Polygon):
    """Simulates wildfire risk using another polygon."""
    wildfire_zone = Polygon([
        (-107.0, 35.0),
        (-107.0, 37.0),
        (-105.0, 37.0),
        (-105.0, 35.0),
    ])

    inter_area = geom.intersection(wildfire_zone).area
    parcel_area = geom.area
    fraction = inter_area / parcel_area if parcel_area > 0 else 0

    score = fraction * 100

    details = {
        "intersection_area": inter_area,
        "parcel_area": parcel_area,
        "fraction_in_wildfire_zone": fraction,
    }

    return score, details


def calculate_overall_score(pillars: List[PillarScore]):
    if not pillars:
        return 0
    return sum(p.score for p in pillars) / len(pillars)


# ----------------------------
# API Endpoints
# ----------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "db": "mock-ok",
        "external_apis": {
            "fema": "mock-ok",
            "usfs": "mock-ok"
        },
        "system_status_text": "Demo backend online"
    }


@app.post("/generate-report", response_model=GenerateReportResponse)
def generate_report(payload: GenerateReportRequest):
    try:
        geom = shape(payload.geometry)
    except Exception as e:
        raise ValueError(f"Invalid geometry: {e}")

    flood_score, flood_details = compute_flood_risk(geom)
    wildfire_score, wildfire_details = compute_wildfire_risk(geom)

    pillars = [
        PillarScore(name="Flood Risk", score=flood_score, details=flood_details),
        PillarScore(name="Wildfire Risk", score=wildfire_score, details=wildfire_details),
    ]

    overall = calculate_overall_score(pillars)

    report_id = str(uuid.uuid4())
    created_at = dt.datetime.utcnow().isoformat() + "Z"

    pdf_url = f"https://demo.example.com/reports/{report_id}.pdf"
    kmz_url = f"https://demo.example.com/reports/{report_id}.kmz"

    return GenerateReportResponse(
        report_id=report_id,
        created_at=created_at,
        overall_risk_score=overall,
        pillars=pillars,
        pdf_url=pdf_url,
        kmz_url=kmz_url,
    )
