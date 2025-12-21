"""Main Signal Fusion Engine orchestrator"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from src.database.models import Candidate, Signal
from src.signal_fusion.collectors import SignalCollector
from src.signal_fusion.scorer import OpennessScorer
from src.config import settings
from datetime import datetime


class SignalFusionEngine:
    """Main engine that orchestrates signal collection and scoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.collector = SignalCollector()
        self.scorer = OpennessScorer()
    
    def run_fusion(
        self,
        industry: str,
        role_level: str = "VP",
        min_score: int = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Run full signal fusion pipeline:
        1. Collect signals from all sources
        2. Score candidates for openness
        3. Store in database
        4. Return high-scoring candidates
        """
        if min_score is None:
            min_score = settings.min_openness_score
        
        # Step 1: Collect signals
        print(f"Collecting signals for {industry} {role_level} candidates...")
        raw_signals = self.collector.collect_all_signals(industry, role_level, limit * 2)
        
        # Step 2: Group signals by candidate
        candidates_with_signals = self._group_signals_by_candidate(raw_signals)
        
        # Step 3: Score each candidate
        print(f"Scoring {len(candidates_with_signals)} candidates...")
        scored_candidates = self.scorer.batch_score(candidates_with_signals)
        
        # Step 4: Filter by minimum score
        high_score_candidates = [
            c for c in scored_candidates
            if c["scoring"]["openness_score"] >= min_score
        ]
        
        # Step 5: Store in database
        print(f"Storing {len(high_score_candidates)} high-scoring candidates...")
        stored_candidates = []
        for item in high_score_candidates:
            candidate_data = item["candidate"]
            signals_data = item["signals"]
            scoring = item["scoring"]
            
            # Create or update candidate
            candidate = self._create_or_update_candidate(candidate_data, scoring)
            
            # Store signals
            for signal_data in signals_data:
                self._create_signal(candidate.id, signal_data)
            
            stored_candidates.append({
                "candidate_id": candidate.id,
                "name": f"{candidate.first_name} {candidate.last_name}",
                "title": candidate.current_title,
                "company": candidate.current_company,
                "openness_score": candidate.openness_score,
                "reasoning": scoring.get("reasoning", "")
            })
        
        self.db.commit()
        
        return stored_candidates
    
    def _group_signals_by_candidate(self, raw_signals: List[Dict]) -> List[Dict]:
        """Group signals by candidate (deduplicate candidates)"""
        candidates_map = {}
        
        for signal in raw_signals:
            # Extract candidate identifier
            linkedin_url = signal.get("linkedin_url") or signal.get("profile_url")
            email = signal.get("email")
            name = signal.get("name", "").split()
            
            if not linkedin_url and not email:
                continue
            
            # Use LinkedIn URL as key if available
            key = linkedin_url or email
            
            if key not in candidates_map:
                candidates_map[key] = {
                    "candidate": {
                        "first_name": name[0] if len(name) > 0 else "",
                        "last_name": " ".join(name[1:]) if len(name) > 1 else "",
                        "email": email or "",
                        "linkedin_url": linkedin_url or "",
                        "current_title": signal.get("current_title", ""),
                        "current_company": signal.get("current_company", ""),
                        "location": signal.get("location", "")
                    },
                    "signals": []
                }
            
            # Add signal
            candidates_map[key]["signals"].append({
                "source": signal.get("source", "unknown"),
                "signal_type": signal.get("signal_type", "unknown"),
                "content": signal.get("content", ""),
                "signal_data": signal.get("signal_data", {})
            })
        
        return list(candidates_map.values())
    
    def _create_or_update_candidate(self, candidate_data: Dict, scoring: Dict) -> Candidate:
        """Create or update candidate in database"""
        linkedin_url = candidate_data.get("linkedin_url")
        email = candidate_data.get("email")
        
        # Try to find existing candidate
        if linkedin_url:
            candidate = self.db.query(Candidate).filter(
                Candidate.linkedin_url == linkedin_url
            ).first()
        elif email:
            candidate = self.db.query(Candidate).filter(
                Candidate.email == email
            ).first()
        else:
            candidate = None
        
        # Create or update
        if candidate:
            candidate.openness_score = scoring["openness_score"]
            candidate.last_score_update = datetime.utcnow()
            # Update other fields if provided
            if candidate_data.get("current_title"):
                candidate.current_title = candidate_data["current_title"]
            if candidate_data.get("current_company"):
                candidate.current_company = candidate_data["current_company"]
        else:
            candidate = Candidate(
                first_name=candidate_data.get("first_name", ""),
                last_name=candidate_data.get("last_name", ""),
                email=candidate_data.get("email", ""),
                linkedin_url=candidate_data.get("linkedin_url", ""),
                current_title=candidate_data.get("current_title", ""),
                current_company=candidate_data.get("current_company", ""),
                location=candidate_data.get("location", ""),
                openness_score=scoring["openness_score"],
                last_score_update=datetime.utcnow()
            )
            self.db.add(candidate)
        
        self.db.flush()
        return candidate
    
    def _create_signal(self, candidate_id: int, signal_data: Dict):
        """Create signal record in database"""
        signal = Signal(
            candidate_id=candidate_id,
            source=signal_data.get("source", "unknown"),
            signal_type=signal_data.get("signal_type", "unknown"),
            content=signal_data.get("content", ""),
            signal_data=signal_data.get("signal_data", {}),
            signal_score=0.0,  # Could calculate individual signal contribution
            confidence=0.5
        )
        self.db.add(signal)

