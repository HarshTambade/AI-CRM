from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import enum

class ContactType(str, enum.Enum):
    CUSTOMER = "customer"
    PROSPECT = "prospect"
    PARTNER = "partner"
    VENDOR = "vendor"

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(20))
    company = Column(String(255))
    job_title = Column(String(100))
    contact_type = Column(Enum(ContactType), default=ContactType.PROSPECT)
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Additional info
    website = Column(String(255))
    linkedin = Column(String(255))
    twitter = Column(String(255))
    notes = Column(Text)
    
    # AI Scoring
    lead_score = Column(Float, default=0.0)
    churn_risk = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", back_populates="contacts")
    leads = relationship("Lead", back_populates="contact")
    opportunities = relationship("Opportunity", back_populates="contact")
    activities = relationship("Activity", back_populates="contact")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.first_name} {self.last_name}')>"

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    
    # Lead details
    source = Column(String(100))  # website, referral, cold_call, etc.
    campaign = Column(String(100))
    budget = Column(Float)
    timeline = Column(String(100))
    
    # AI Scoring
    lead_score = Column(Float, default=0.0)
    conversion_probability = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="leads")
    assigned_to = relationship("User", back_populates="leads")
    activities = relationship("Activity", back_populates="lead")
    
    def __repr__(self):
        return f"<Lead(id={self.id}, status='{self.status}', score={self.lead_score})>" 