"""Script to generate outreach campaigns"""

import argparse
import sys
from src.database.database import SessionLocal
from src.outreach.campaign import OutreachCampaignManager
from src.database.models import Candidate, OutreachCampaign


def main():
    parser = argparse.ArgumentParser(description="Generate outreach campaigns")
    parser.add_argument("--campaign-id", type=int, help="Generate specific campaign (if exists)")
    parser.add_argument("--candidate-id", type=int, help="Generate for specific candidate")
    parser.add_argument("--job-opening-id", type=int, help="Optional job opening ID")
    parser.add_argument("--batch", action="store_true", help="Generate for all high-score candidates")
    parser.add_argument("--min-score", type=float, default=70.0, help="Minimum score for batch")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        manager = OutreachCampaignManager(db)
        
        if args.campaign_id:
            # View existing campaign
            campaign = db.query(OutreachCampaign).filter(OutreachCampaign.id == args.campaign_id).first()
            if campaign:
                print(f"\nCampaign {args.campaign_id}:")
                print(f"Subject: {campaign.subject}")
                print(f"\nBody:\n{campaign.body}")
                print(f"\nStatus: {campaign.status}")
            else:
                print(f"Campaign {args.campaign_id} not found")
        
        elif args.candidate_id:
            # Generate for specific candidate
            campaign = manager.create_campaign(args.candidate_id, args.job_opening_id)
            print(f"\n✅ Created campaign {campaign.id}")
            print(f"Subject: {campaign.subject}")
            print(f"\nBody:\n{campaign.body}")
        
        elif args.batch:
            # Generate for all high-score candidates
            candidates = db.query(Candidate).filter(
                Candidate.openness_score >= args.min_score,
                Candidate.status == "identified"
            ).all()
            
            print(f"Generating campaigns for {len(candidates)} candidates...")
            campaigns = manager.batch_create_campaigns(
                [c.id for c in candidates],
                args.job_opening_id
            )
            print(f"✅ Created {len(campaigns)} campaigns")
        
        else:
            print("Error: Must specify --candidate-id, --campaign-id, or --batch")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

