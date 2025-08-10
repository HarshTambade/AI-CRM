from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.database import get_db
from app.models.opportunity import Activity, ActivityType

router = APIRouter()

class ActivityCreate(BaseModel):
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    activity_type: ActivityType
    subject: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None
    direction: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None

class ActivityUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None
    direction: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None

class ActivityResponse(BaseModel):
    id: int
    user_id: int
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    activity_type: ActivityType
    subject: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None
    direction: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    sentiment_score: float
    key_topics: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new activity."""
    activity = Activity(
        **activity_data.dict(),
        user_id=current_user.id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

@router.get("/", response_model=List[ActivityResponse])
async def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    activity_type: Optional[ActivityType] = None,
    contact_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activities with optional filtering."""
    query = db.query(Activity)
    
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    
    if contact_id:
        query = query.filter(Activity.contact_id == contact_id)
    
    activities = query.offset(skip).limit(limit).all()
    return activities

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity by ID."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    for field, value in activity_data.dict(exclude_unset=True).items():
        setattr(activity, field, value)
    
    db.commit()
    db.refresh(activity)
    return activity

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(activity)
    db.commit()
    return {"message": "Activity deleted successfully"} 