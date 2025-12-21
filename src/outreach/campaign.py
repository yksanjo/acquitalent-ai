"""Outreach campaign management"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.models import Candidate, OutreachCampaign, JobOpening
from src.outreach.generator import OutreachGenerator


class OutreachCampaignManager:
    """Manage outreach campaigns to candidates"""
    
    def __init__(self, db: Session):
        self.db = db
        self.generator = OutreachGenerator()
    
    def create_campaign(
        self,
        candidate_id: int,
        job_opening_id: Optional[int] = None
    ) -> OutreachCampaign:
        """Create and generate outreach campaign for a candidate"""
        
        # Get candidate
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Get job opening if provided
        job_opening = None
        if job_opening_id:
            job_opening = self.db.query(JobOpening).filter(JobOpening.id == job_opening_id).first()
        
        # Get candidate signals for personalization
        signals = [
            {
                "source": s.source,
                "signal_type": s.signal_type,
                "content": s.content,
                "signal_data": s.signal_data
            }
            for s in candidate.signals
        ]
        
        # Prepare data for generator
        candidate_data = {
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "current_title": candidate.current_title,
            "current_company": candidate.current_company,
            "email": candidate.email,
            "linkedin_url": candidate.linkedin_url
        }
        
        job_data = None
        if job_opening:
            job_data = {
                "title": job_opening.title,
                "requirements": job_opening.requirements,
                "client": {
                    "company_name": job_opening.client.company_name,
                    "company_stage": job_opening.client.company_stage
                }
            }
        
        # Generate email
        email = self.generator.generate_email(candidate_data, job_data, signals)
        
        # Create campaign record
        campaign = OutreachCampaign(
            candidate_id=candidate_id,
            job_opening_id=job_opening_id,
            subject=email["subject"],
            body=email["body"],
            personalization_data=email["personalization_data"],
            status="draft"
        )
        
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        
        return campaign
    
    def send_campaign(self, campaign_id: int) -> bool:
        """
        Send outreach campaign via email service
        Returns True if sent successfully
        """
        campaign = self.db.query(OutreachCampaign).filter(
            OutreachCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status != "draft":
            raise ValueError(f"Campaign {campaign_id} already sent")
        
        # TODO: Integrate with Instantly.ai or Smartlead
        # For MVP, mark as sent
        campaign.status = "sent"
        campaign.sent_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def batch_create_campaigns(
        self,
        candidate_ids: List[int],
        job_opening_id: Optional[int] = None
    ) -> List[OutreachCampaign]:
        """Create multiple outreach campaigns"""
        campaigns = []
        for candidate_id in candidate_ids:
            try:
                campaign = self.create_campaign(candidate_id, job_opening_id)
                campaigns.append(campaign)
            except Exception as e:
                print(f"Error creating campaign for candidate {candidate_id}: {e}")
                continue
        
        return campaigns

