from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.database import get_db
from app.models.contact import Lead, LeadStatus

router = APIRouter()

class LeadCreate(BaseModel):
    contact_id: int
    assigned_to_id: Optional[int] = None
    status: LeadStatus = LeadStatus.NEW
    source: Optional[str] = None
    campaign: Optional[str] = None
    budget: Optional[float] = None
    timeline: Optional[str] = None

class LeadUpdate(BaseModel):
    assigned_to_id: Optional[int] = None
    status: Optional[LeadStatus] = None
    source: Optional[str] = None
    campaign: Optional[str] = None
    budget: Optional[float] = None
    timeline: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    contact_id: int
    assigned_to_id: Optional[int] = None
    status: LeadStatus
    source: Optional[str] = None
    campaign: Optional[str] = None
    budget: Optional[float] = None
    timeline: Optional[str] = None
    lead_score: float
    conversion_probability: float
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead."""
    lead = Lead(**lead_data.dict())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[LeadStatus] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leads with optional filtering."""
    query = db.query(Lead)
    
    if status:
        query = query.filter(Lead.status == status)
    
    leads = query.offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    for field, value in lead_data.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    return lead

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted successfully"} 