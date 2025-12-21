"""FastAPI application for AcquiTalent AI"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from src.database.database import get_db, init_db
from src.signal_fusion.engine import SignalFusionEngine
from src.outreach.campaign import OutreachCampaignManager
from src.database.models import Candidate, Client, JobOpening, OutreachCampaign

app = FastAPI(title="AcquiTalent AI API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class CandidateResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    current_title: Optional[str]
    current_company: Optional[str]
    openness_score: float
    
    class Config:
        from_attributes = True


class SignalFusionRequest(BaseModel):
    industry: str
    role_level: str = "VP"
    min_score: int = 70
    limit: int = 50


class JobOpeningCreate(BaseModel):
    client_id: int
    title: str
    department: Optional[str] = None
    requirements: Optional[str] = None


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check
@app.get("/")
async def root():
    return {"message": "AcquiTalent AI API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Signal Fusion endpoints
@app.post("/api/signal-fusion/run")
async def run_signal_fusion(
    request: SignalFusionRequest,
    db: Session = Depends(get_db)
):
    """Run signal fusion engine to find high-scoring candidates"""
    engine = SignalFusionEngine(db)
    candidates = engine.run_fusion(
        industry=request.industry,
        role_level=request.role_level,
        min_score=request.min_score,
        limit=request.limit
    )
    return {"candidates": candidates, "count": len(candidates)}


# Candidate endpoints
@app.get("/api/candidates", response_model=List[CandidateResponse])
async def get_candidates(
    min_score: Optional[float] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get candidates, optionally filtered by minimum openness score"""
    query = db.query(Candidate)
    if min_score:
        query = query.filter(Candidate.openness_score >= min_score)
    candidates = query.order_by(Candidate.openness_score.desc()).limit(limit).all()
    return candidates


@app.get("/api/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# Outreach endpoints
@app.post("/api/outreach/campaigns")
async def create_outreach_campaign(
    candidate_id: int,
    job_opening_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Create an outreach campaign for a candidate"""
    manager = OutreachCampaignManager(db)
    campaign = manager.create_campaign(candidate_id, job_opening_id)
    return {
        "id": campaign.id,
        "subject": campaign.subject,
        "body": campaign.body,
        "status": campaign.status
    }


@app.post("/api/outreach/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Send an outreach campaign"""
    manager = OutreachCampaignManager(db)
    success = manager.send_campaign(campaign_id)
    return {"success": success, "campaign_id": campaign_id}


# Client and Job Opening endpoints
@app.post("/api/clients")
async def create_client(
    company_name: str,
    contact_name: Optional[str] = None,
    contact_email: Optional[str] = None,
    company_stage: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new client"""
    client = Client(
        company_name=company_name,
        contact_name=contact_name,
        contact_email=contact_email,
        company_stage=company_stage,
        industry=industry
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"id": client.id, "company_name": client.company_name}


@app.post("/api/job-openings")
async def create_job_opening(
    job: JobOpeningCreate,
    db: Session = Depends(get_db)
):
    """Create a new job opening"""
    job_opening = JobOpening(
        client_id=job.client_id,
        title=job.title,
        department=job.department,
        requirements=job.requirements
    )
    db.add(job_opening)
    db.commit()
    db.refresh(job_opening)
    return {"id": job_opening.id, "title": job_opening.title}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

