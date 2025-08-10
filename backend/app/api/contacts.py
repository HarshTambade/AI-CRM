from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.database import get_db
from app.models.contact import Contact, ContactType

router = APIRouter()

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: ContactType = ContactType.PROSPECT
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: Optional[ContactType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    notes: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: ContactType
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    notes: Optional[str] = None
    lead_score: float
    churn_risk: float
    sentiment_score: float
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contact."""
    contact = Contact(
        **contact_data.dict(),
        created_by_id=current_user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    contact_type: Optional[ContactType] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contacts with optional filtering."""
    query = db.query(Contact)
    
    if search:
        query = query.filter(
            (Contact.first_name.contains(search)) |
            (Contact.last_name.contains(search)) |
            (Contact.email.contains(search)) |
            (Contact.company.contains(search))
        )
    
    if contact_type:
        query = query.filter(Contact.contact_type == contact_type)
    
    contacts = query.offset(skip).limit(limit).all()
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contact by ID."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for field, value in contact_data.dict(exclude_unset=True).items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"} 