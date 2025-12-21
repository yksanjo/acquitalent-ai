"""Database models for AcquiTalent AI"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Candidate(Base):
    """Executive candidate profile"""
    
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    linkedin_url = Column(String)
    current_title = Column(String)
    current_company = Column(String)
    location = Column(String)
    
    # Openness scoring
    openness_score = Column(Float, default=0.0)
    last_score_update = Column(DateTime, default=datetime.utcnow)
    
    # Status
    status = Column(String, default="identified")  # identified, contacted, interested, interviewing, placed
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    signals = relationship("Signal", back_populates="candidate", cascade="all, delete-orphan")
    outreach_campaigns = relationship("OutreachCampaign", back_populates="candidate")
    placements = relationship("Placement", back_populates="candidate")


class Signal(Base):
    """Passive interest signal from various sources"""
    
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    
    # Signal details
    source = Column(String, nullable=False)  # linkedin, podcast, substack, twitter, conference
    signal_type = Column(String, nullable=False)  # job_change_network, podcast_appearance, article, follow, speaking
    content = Column(Text)  # Raw content or URL
    signal_data = Column(JSON)  # Structured data from signal
    
    # Scoring
    signal_score = Column(Float, default=0.0)  # 0-100 contribution to openness
    confidence = Column(Float, default=0.0)  # 0-1 confidence in signal validity
    
    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="signals")


class Client(Base):
    """Client company hiring executives"""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    contact_name = Column(String)
    contact_email = Column(String)
    company_stage = Column(String)  # Series B, Series C, PE-backed, etc.
    industry = Column(String)
    
    # Status
    status = Column(String, default="prospect")  # prospect, pilot, active, closed
    pilot_agreement_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_openings = relationship("JobOpening", back_populates="client")
    placements = relationship("Placement", back_populates="client")


class JobOpening(Base):
    """Open executive role at a client"""
    
    __tablename__ = "job_openings"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    title = Column(String, nullable=False)  # VP Engineering, VP Sales, etc.
    department = Column(String)
    requirements = Column(Text)
    status = Column(String, default="open")  # open, sourcing, interviewing, filled, closed
    
    # Timeline
    target_fill_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="job_openings")
    candidate_matches = relationship("CandidateMatch", back_populates="job_opening")


class CandidateMatch(Base):
    """Match between candidate and job opening"""
    
    __tablename__ = "candidate_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"), nullable=False)
    
    # Match scoring
    fit_score = Column(Float, default=0.0)  # 0-100 how well candidate fits role
    match_reason = Column(Text)  # AI-generated explanation
    
    # Status
    status = Column(String, default="matched")  # matched, presented, interviewing, offer, declined
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate")
    job_opening = relationship("JobOpening", back_populates="candidate_matches")


class OutreachCampaign(Base):
    """Email outreach campaign to candidate"""
    
    __tablename__ = "outreach_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"), nullable=True)
    
    # Email details
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    personalization_data = Column(JSON)  # Data used for personalization
    
    # Status
    status = Column(String, default="draft")  # draft, sent, opened, replied, bounced
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    replied_at = Column(DateTime)
    reply_content = Column(Text)
    
    # Metrics
    open_rate = Column(Boolean, default=False)
    reply_rate = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="outreach_campaigns")


class Placement(Base):
    """Successful placement of candidate at client"""
    
    __tablename__ = "placements"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"), nullable=True)
    
    # Financial
    placement_fee = Column(Float, nullable=False)  # $50k for VP+, $25k for director
    fee_status = Column(String, default="pending")  # pending, invoiced, paid
    
    # Timeline
    offer_date = Column(DateTime)
    start_date = Column(DateTime)
    invoiced_at = Column(DateTime)
    paid_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="placements")
    client = relationship("Client", back_populates="placements")

