"""AI-powered email outreach generation"""

import anthropic
from typing import Dict, Optional, List
from src.config import settings


class OutreachGenerator:
    """Generate hyper-personalized outreach emails"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def generate_email(
        self,
        candidate: Dict,
        job_opening: Optional[Dict] = None,
        signals: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate personalized outreach email
        Returns: {
            "subject": "...",
            "body": "...",
            "personalization_data": {...}
        }
        """
        prompt = self._build_email_prompt(candidate, job_opening, signals)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            email_text = response.content[0].text
            return self._parse_email_response(email_text, candidate, job_opening, signals)
            
        except Exception as e:
            # Fallback template
            return self._generate_fallback_email(candidate, job_opening)
    
    def _build_email_prompt(
        self,
        candidate: Dict,
        job_opening: Optional[Dict],
        signals: Optional[List[Dict]]
    ) -> str:
        """Build prompt for Claude to generate email"""
        
        candidate_info = f"""
Candidate: {candidate.get('first_name', '')} {candidate.get('last_name', '')}
Current Role: {candidate.get('current_title', 'Unknown')}
Current Company: {candidate.get('current_company', 'Unknown')}
"""
        
        job_info = ""
        if job_opening:
            job_info = f"""
Job Opening:
- Title: {job_opening.get('title', 'Unknown')}
- Company: {job_opening.get('client', {}).get('company_name', 'Unknown')}
- Stage: {job_opening.get('client', {}).get('company_stage', 'Unknown')}
- Requirements: {job_opening.get('requirements', 'Not specified')}
"""
        
        signals_info = ""
        if signals:
            signals_text = "\n".join([
                f"- {s.get('source')}: {s.get('content', '')[:150]}"
                for s in signals[:3]  # Top 3 signals
            ])
            signals_info = f"""
Signals detected (why we think they might be open):
{signals_text}
"""
        
        prompt = f"""
You are a top-tier executive recruiter writing a personalized outreach email. 
The goal is to get a reply and start a conversation, not to sell immediately.

{candidate_info}
{job_info}
{signals_info}

Write a short, authentic email that:
1. Opens with a specific, genuine compliment about their work/content (reference the signals)
2. Briefly mentions the opportunity (if job_opening provided) or just says you work with interesting companies
3. Asks if they're open to exploring (low pressure)
4. Ends with a simple question to encourage reply

Tone: Professional but warm, like a peer reaching out, not a salesperson
Length: 4-6 sentences max
Hook: Reference something specific from their content/signals

Format your response as:
SUBJECT: [subject line]
BODY:
[email body]

The subject should be personal and intriguing, like:
"[First Name] - Impressed by your [specific thing]"
or
"[First Name] - [Company] opportunity?"
"""
        return prompt
    
    def _parse_email_response(
        self,
        email_text: str,
        candidate: Dict,
        job_opening: Optional[Dict],
        signals: Optional[List[Dict]]
    ) -> Dict:
        """Parse Claude's email response"""
        import re
        
        # Extract subject
        subject_match = re.search(r'SUBJECT:\s*(.+)', email_text, re.IGNORECASE)
        subject = subject_match.group(1).strip() if subject_match else f"{candidate.get('first_name', 'Candidate')} - Opportunity?"
        
        # Extract body
        body_match = re.search(r'BODY:\s*(.+?)(?:\n\n|\Z)', email_text, re.DOTALL | re.IGNORECASE)
        if not body_match:
            # Try alternative format
            body_match = re.search(r'(?:BODY|EMAIL):\s*(.+)', email_text, re.DOTALL | re.IGNORECASE)
        
        body = body_match.group(1).strip() if body_match else email_text.strip()
        
        # Clean up body (remove markdown if present)
        body = re.sub(r'\*\*(.+?)\*\*', r'\1', body)  # Remove bold
        body = re.sub(r'_(.+?)_', r'\1', body)  # Remove italic
        
        return {
            "subject": subject,
            "body": body,
            "personalization_data": {
                "candidate_name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}",
                "signals_used": [s.get('source') for s in (signals or [])[:3]],
                "job_title": job_opening.get('title') if job_opening else None
            }
        }
    
    def _generate_fallback_email(
        self,
        candidate: Dict,
        job_opening: Optional[Dict]
    ) -> Dict:
        """Fallback email template if AI fails"""
        first_name = candidate.get('first_name', 'there')
        title = candidate.get('current_title', 'executive')
        company = candidate.get('current_company', 'your company')
        
        subject = f"{first_name} - Impressed by your work at {company}"
        
        client_name = "some interesting companies"
        if job_opening and job_opening.get('client'):
            client_name = job_opening['client'].get('company_name', client_name)
        
        body = f"""Hey {first_name},

Caught your work at {company} - really impressive what you've built as {title}.

I work with {client_name} that are scaling. Not sure if you're open to exploring, but thought there might be alignment.

Worth a 15-min conversation?

Best,
[Your Name]
Talent Partner @ AcquiTalent
"""
        
        return {
            "subject": subject,
            "body": body,
            "personalization_data": {
                "candidate_name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}",
                "fallback": True
            }
        }

