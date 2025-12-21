"""AI-powered scoring engine for candidate openness"""

import anthropic
from typing import List, Dict, Optional
from src.config import settings


class OpennessScorer:
    """Score candidates on 0-100 scale for openness to new opportunities"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def score_candidate(self, candidate_data: Dict, signals: List[Dict]) -> Dict:
        """
        Score a single candidate based on their signals
        Returns: {
            "openness_score": 0-100,
            "confidence": 0-1,
            "reasoning": "explanation",
            "key_signals": [...]
        }
        """
        # Build prompt for Claude
        prompt = self._build_scoring_prompt(candidate_data, signals)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            result = self._parse_scoring_response(response.content[0].text)
            return result
            
        except Exception as e:
            # Fallback scoring if API fails
            return self._fallback_score(signals)
    
    def _build_scoring_prompt(self, candidate_data: Dict, signals: List[Dict]) -> str:
        """Build the prompt for Claude to score candidate"""
        
        candidate_info = f"""
Candidate: {candidate_data.get('first_name', '')} {candidate_data.get('last_name', '')}
Current Role: {candidate_data.get('current_title', 'Unknown')}
Current Company: {candidate_data.get('current_company', 'Unknown')}
"""
        
        signals_text = "\n".join([
            f"- {s.get('source', 'unknown')}: {s.get('signal_type', 'unknown')} - {s.get('content', '')[:200]}"
            for s in signals
        ])
        
        prompt = f"""
You are an expert executive recruiter analyzing passive interest signals to determine if an executive is open to new opportunities.

{candidate_info}

Signals detected:
{signals_text}

Score this candidate on a 0-100 scale for "openness to new opportunities" based on these signals.

Scoring guidelines:
- 0-30: Stable, no signals of movement
- 31-50: Some activity but likely staying put
- 51-70: Moderate signals, possibly open if right opportunity
- 71-85: Strong signals, likely open to exploring
- 86-100: Very strong signals, actively considering change

Consider:
1. Recency of signals (recent = higher score)
2. Signal strength (job change in network > casual post)
3. Signal diversity (multiple sources = higher confidence)
4. Industry context (is this normal activity or unusual?)

Respond in JSON format:
{{
    "openness_score": <0-100>,
    "confidence": <0-1>,
    "reasoning": "<2-3 sentence explanation>",
    "key_signals": ["<signal1>", "<signal2>"]
}}
"""
        return prompt
    
    def _parse_scoring_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response"""
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    "openness_score": float(result.get("openness_score", 0)),
                    "confidence": float(result.get("confidence", 0.5)),
                    "reasoning": result.get("reasoning", ""),
                    "key_signals": result.get("key_signals", [])
                }
            except:
                pass
        
        # Fallback if parsing fails
        return {
            "openness_score": 50.0,
            "confidence": 0.3,
            "reasoning": "Unable to parse AI response",
            "key_signals": []
        }
    
    def _fallback_score(self, signals: List[Dict]) -> Dict:
        """Fallback scoring if AI fails"""
        if not signals:
            return {
                "openness_score": 0.0,
                "confidence": 0.0,
                "reasoning": "No signals detected",
                "key_signals": []
            }
        
        # Simple heuristic scoring
        score = min(len(signals) * 15, 100)
        return {
            "openness_score": float(score),
            "confidence": 0.5,
            "reasoning": f"Fallback scoring based on {len(signals)} signals",
            "key_signals": [s.get("signal_type", "unknown") for s in signals[:3]]
        }
    
    def batch_score(self, candidates_with_signals: List[Dict]) -> List[Dict]:
        """Score multiple candidates efficiently"""
        results = []
        for item in candidates_with_signals:
            candidate = item.get("candidate", {})
            signals = item.get("signals", [])
            score_result = self.score_candidate(candidate, signals)
            results.append({
                "candidate": candidate,
                "signals": signals,
                "scoring": score_result
            })
        return results

