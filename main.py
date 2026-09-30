import json
from database import ComplaintModel, SessionLocal, init_db
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

app = FastAPI(
    title="Govspot DPI Engine",
    description=(
        "Autonomous Demand-to-Deployment Infrastructure Backend & Procurement"
        " API"
    ),
    version="3.0",
)

# Enable CORS for public access and UI communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for database session
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


class IngestionPayload(BaseModel):
  raw_message: str
  latitude: float
  longitude: float
  severity_score: int


def calculate_coi_bleed(severity: int, issue_type: str) -> float:
  """Calculates the daily financial Cost-of-Inaction bleed based on severity and category."""
  base_multipliers = {
      "bridge_failure": 15000.0,
      "road_collapse": 8000.0,
      "water_main_burst": 6000.0,
      "general_infrastructure": 3000.0,
  }
  multiplier = base_multipliers.get(issue_type, 4000.0)
  return round(severity * multiplier, 2)


@app.on_event("startup")
def startup_event():
  init_db()


@app.post("/ingest", status_code=201)
def ingest_signal(payload: IngestionPayload, db: Session = Depends(get_db)):
  msg_lower = payload.raw_message.lower()

  # Heuristic category classification
  if "bridge" in msg_lower or "pillar" in msg_lower:
    issue_type = "bridge_failure"
  elif "road" in msg_lower or "pothole" in msg_lower or "cracking" in msg_lower:
    issue_type = "road_collapse"
  elif "water" in msg_lower or "pipe" in msg_lower or "flood" in msg_lower:
    issue_type = "water_main_burst"
  else:
    issue_type = "general_infrastructure"

  coi_bleed = calculate_coi_bleed(payload.severity_score, issue_type)

  db_complaint = ComplaintModel(
      issue_type=issue_type,
      description=payload.raw_message,
      latitude=payload.latitude,
      longitude=payload.longitude,
      severity_score=payload.severity_score,
      coi_financial_bleed=coi_bleed,
      status="Pending Analysis",
  )

  db.add(db_complaint)
  db.commit()
  db.refresh(db_complaint)

  return {
      "status": "success",
      "message_id": db_complaint.id,
      "extracted_category": issue_type,
      "daily_cost_of_inaction_usd": coi_bleed,
  }


@app.get("/complaints")
def get_complaints(db: Session = Depends(get_db)):
  complaints = db.query(ComplaintModel).all()
  return complaints


@app.post("/generate-tender/{complaint_id}")
def generate_tender(complaint_id: int, db: Session = Depends(get_db)):
  complaint = (
      db.query(ComplaintModel)
      .filter(ComplaintModel.id == complaint_id)
      .first()
  )
  if not complaint:
    raise HTTPException(status_code=404, detail="Complaint not found")

  # Algorithmic Bill of Materials (BOM) generation
  budget = complaint.severity_score * 12500.0
  bom = {
      "materials": [
          {"item": "High-Grade Reinforced Concrete Mix", "quantity": "45 Tons"},
          {
              "item": "Structural Steel Support Beams",
              "quantity": f"{complaint.severity_score * 3} Units",
          },
          {"item": "Heavy Machinery & Excavation Fleet", "quantity": "2 Days"},
      ],
      "labor_man_hours": int(120 * complaint.severity_score),
  }

  complaint.status = "Tender Drafted"
  db.commit()

  return {
      "tender_id": f"TND-2026-{complaint.id:04d}",
      "project_title": (
          f"Emergency Restoration: {complaint.issue_type.replace('_', ' ').title()}"
      ),
      "estimated_budget_usd": budget,
      "procurement_justification": (
          f"Triggered by daily economic bleed rate of"
          f" ${complaint.coi_financial_bleed:,.2f}/day and severity index"
          f" {complaint.severity_score}/10."
      ),
      "bill_of_materials": bom,
      "status": "Ready for Executive Sign-off",
  }