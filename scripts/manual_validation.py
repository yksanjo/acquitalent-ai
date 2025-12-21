"""Manual validation script - find candidates and test outreach manually"""

import argparse
import sys
from src.database.database import SessionLocal
from src.signal_fusion.engine import SignalFusionEngine
from src.outreach.campaign import OutreachCampaignManager


def main():
    parser = argparse.ArgumentParser(description="Manual validation - find candidates and generate outreach")
    parser.add_argument("--industry", type=str, required=True, help="Industry (e.g., fintech, SaaS)")
    parser.add_argument("--role", type=str, default="VP Engineering", help="Target role")
    parser.add_argument("--limit", type=int, default=10, help="Number of candidates to find")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        print(f"🔍 Finding {args.limit} {args.role} candidates in {args.industry}...")
        
        # Run signal fusion
        engine = SignalFusionEngine(db)
        candidates = engine.run_fusion(
            industry=args.industry,
            role_level=args.role.split()[0],  # Extract "VP" from "VP Engineering"
            limit=args.limit
        )
        
        if not candidates:
            print("❌ No candidates found. Check your data sources.")
            return
        
        print(f"\n✅ Found {len(candidates)} candidates")
        print("\n" + "="*60)
        
        # Generate outreach for each
        manager = OutreachCampaignManager(db)
        
        for i, candidate_info in enumerate(candidates, 1):
            candidate_id = candidate_info["candidate_id"]
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            
            print(f"\n📧 Candidate {i}: {candidate_info['name']}")
            print(f"   {candidate_info['title']} @ {candidate_info['company']}")
            print(f"   Score: {candidate_info['openness_score']:.1f}")
            
            # Generate email
            campaign = manager.create_campaign(candidate_id)
            
            print(f"\n   Subject: {campaign.subject}")
            print(f"\n   Body:\n   {campaign.body.replace(chr(10), chr(10) + '   ')}")
            print(f"\n   Email: {candidate.email or 'N/A'}")
            print(f"   LinkedIn: {candidate.linkedin_url or 'N/A'}")
            print("\n" + "-"*60)
        
        print(f"\n✅ Generated {len(candidates)} outreach emails")
        print("\n📋 Next steps:")
        print("   1. Review each email for quality")
        print("   2. Send manually (copy/paste) to test response rates")
        print("   3. Target: 3+ positive replies (30%+ reply rate)")
        print("   4. If <10% replies, refine messaging before automating")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

