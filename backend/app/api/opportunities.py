from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.database import get_db
from app.models.opportunity import Opportunity, OpportunityStage

router = APIRouter()

class OpportunityCreate(BaseModel):
    contact_id: int
    assigned_to_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "USD"
    probability: float = 0.0
    expected_close_date: Optional[str] = None
    stage: OpportunityStage = OpportunityStage.PROSPECTING

class OpportunityUpdate(BaseModel):
    assigned_to_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    probability: Optional[float] = None
    expected_close_date: Optional[str] = None
    stage: Optional[OpportunityStage] = None

class OpportunityResponse(BaseModel):
    id: int
    contact_id: int
    assigned_to_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    amount: Optional[float] = None
    currency: str
    probability: float
    expected_close_date: Optional[str] = None
    stage: OpportunityStage
    win_probability: float
    risk_score: float
    next_best_action: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=OpportunityResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new opportunity."""
    opportunity = Opportunity(**opportunity_data.dict())
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity

@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    stage: Optional[OpportunityStage] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get opportunities with optional filtering."""
    query = db.query(Opportunity)
    
    if stage:
        query = query.filter(Opportunity.stage == stage)
    
    opportunities = query.offset(skip).limit(limit).all()
    return opportunities

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get opportunity by ID."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update opportunity."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    for field, value in opportunity_data.dict(exclude_unset=True).items():
        setattr(opportunity, field, value)
    
    db.commit()
    db.refresh(opportunity)
    return opportunity

@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete opportunity."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    db.delete(opportunity)
    db.commit()
    return {"message": "Opportunity deleted successfully"} 