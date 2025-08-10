from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import enum

class OpportunityStage(str, enum.Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"
    DEMO = "demo"
    PROPOSAL = "proposal"

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    stage = Column(Enum(OpportunityStage), default=OpportunityStage.PROSPECTING)
    
    # Opportunity details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    amount = Column(Float)
    currency = Column(String(3), default="USD")
    probability = Column(Float, default=0.0)
    expected_close_date = Column(DateTime(timezone=True))
    
    # AI Insights
    win_probability = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    next_best_action = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="opportunities")
    assigned_to = relationship("User", back_populates="opportunities")
    activities = relationship("Activity", back_populates="opportunity")
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, name='{self.name}', stage='{self.stage}')>"

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    
    activity_type = Column(Enum(ActivityType), nullable=False)
    subject = Column(String(255))
    description = Column(Text)
    
    # Activity details
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration = Column(Integer)  # in minutes
    
    # Communication details
    direction = Column(String(20))  # inbound, outbound
    outcome = Column(String(100))
    notes = Column(Text)
    
    # AI Analysis
    sentiment_score = Column(Float, default=0.0)
    key_topics = Column(Text)  # JSON string of extracted topics
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activities")
    contact = relationship("Contact", back_populates="activities")
    lead = relationship("Lead", back_populates="activities")
    opportunity = relationship("Opportunity", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, type='{self.activity_type}', subject='{self.subject}')>"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    
    # Task details
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # AI Suggestions
    suggested_priority = Column(String(20))
    estimated_duration = Column(Integer)  # in minutes
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_to = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>" 