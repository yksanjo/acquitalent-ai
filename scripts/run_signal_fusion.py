"""Script to run signal fusion engine"""

import argparse
import sys
from src.database.database import SessionLocal
from src.signal_fusion.engine import SignalFusionEngine


def main():
    parser = argparse.ArgumentParser(description="Run Signal Fusion Engine")
    parser.add_argument("--industry", type=str, required=True, help="Industry to search (e.g., fintech, SaaS)")
    parser.add_argument("--role-level", type=str, default="VP", help="Role level (VP, Director, etc.)")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum openness score")
    parser.add_argument("--limit", type=int, default=50, help="Maximum candidates to find")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        engine = SignalFusionEngine(db)
        candidates = engine.run_fusion(
            industry=args.industry,
            role_level=args.role_level,
            min_score=args.min_score,
            limit=args.limit
        )
        
        print(f"\n✅ Found {len(candidates)} candidates with score >= {args.min_score}")
        print("\nTop candidates:")
        for i, candidate in enumerate(candidates[:10], 1):
            print(f"{i}. {candidate['name']} - {candidate['title']} @ {candidate['company']}")
            print(f"   Score: {candidate['openness_score']:.1f}")
            print(f"   Reasoning: {candidate['reasoning']}\n")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

