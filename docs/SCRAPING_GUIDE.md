# Scraping Implementation Guide

## Current Status

The scraping collectors are currently **stubbed out** (placeholder functions). This guide shows you how to implement them using real APIs and tools.

---

## 1. LinkedIn Scraping

### Option A: Apify LinkedIn Scraper (Recommended)

**Why Apify:**
- Stays within LinkedIn ToS
- Handles rate limiting
- Pre-built actors available
- Reliable and scalable

**Setup:**
```bash
pip install apify-client
```

**Implementation:**
```python
# src/signal_fusion/collectors.py
from apify_client import ApifyClient
from src.config import settings

class LinkedInCollector:
    def __init__(self):
        self.client = ApifyClient(settings.apify_api_token)
    
    def collect_job_change_signals(self, company: str, role_level: str = "VP") -> List[Dict]:
        """
        Detect job changes in network using Apify LinkedIn Profile Scraper
        """
        # Run Apify actor
        run = self.client.actor("apify/linkedin-profile-scraper").call(
            run_input={
                "startUrls": [
                    {
                        "url": f"https://www.linkedin.com/search/results/people/?keywords={role_level}%20{company}"
                    }
                ],
                "maxItems": 100,
                "extendOutputFunction": """async ({ data, item, helpers, page, customData, label }) => {
                    return item;
                }""",
                "extendScraperFunction": """async ({ page, request, customData, Apify }) => {
                    // Custom logic to detect job changes
                }""",
            }
        )
        
        # Wait for run to finish
        self.client.run(run["defaultDatasetId"]).wait_for_finish()
        
        # Get results
        items = self.client.dataset(run["defaultDatasetId"]).list_items()
        
        signals = []
        for item in items.get("items", []):
            # Detect signals from profile data
            if self._has_job_change_signals(item):
                signals.append({
                    "name": item.get("fullName", ""),
                    "linkedin_url": item.get("url", ""),
                    "current_title": item.get("headline", ""),
                    "current_company": self._extract_company(item),
                    "source": "linkedin",
                    "signal_type": "job_change_network",
                    "content": item.get("summary", ""),
                    "signal_data": {
                        "recent_activity": item.get("recentActivity", []),
                        "connections_count": item.get("connectionsCount", 0)
                    }
                })
        
        return signals
    
    def _has_job_change_signals(self, profile_data: Dict) -> bool:
        """Detect if profile shows job change signals"""
        # Check for recent activity indicating movement
        recent_activity = profile_data.get("recentActivity", [])
        
        # Signal: Recent "Congratulations" comments
        congrats_count = sum(1 for activity in recent_activity 
                           if "congratulat" in activity.get("text", "").lower())
        
        # Signal: Recent profile updates
        profile_updates = sum(1 for activity in recent_activity 
                             if "updated" in activity.get("type", "").lower())
        
        # Signal: New connections to VCs/recruiters
        # (Would need to analyze connections)
        
        return congrats_count >= 3 or profile_updates >= 2
```

**Apify Actors to Use:**
- `apify/linkedin-profile-scraper` - Scrape profiles
- `apify/linkedin-post-scraper` - Scrape posts and comments
- `apify/linkedin-company-scraper` - Scrape company pages

**Cost:** ~$0.10-0.50 per 100 profiles

---

### Option B: PhantomBuster (Alternative)

**Why PhantomBuster:**
- Browser automation (stays within ToS)
- Visual workflow builder
- Good for LinkedIn

**Setup:**
```python
import requests

class LinkedInCollector:
    def __init__(self):
        self.api_key = settings.phantom_buster_api_key
        self.base_url = "https://api.phantombuster.com/api/v2"
    
    def collect_job_change_signals(self, company: str, role_level: str = "VP"):
        # Trigger PhantomBuster agent
        response = requests.post(
            f"{self.base_url}/agents/launch",
            headers={"X-Phantombuster-Key": self.api_key},
            json={
                "id": "your-linkedin-scraper-id",
                "argument": {
                    "searchQuery": f"{role_level} {company}",
                    "numberOfProfiles": 100
                }
            }
        )
        
        # Poll for results
        # ... (implementation)
```

---

## 2. Podcast Scraping

### Option A: Listen Notes API

**Setup:**
```bash
pip install listennotes
```

**Implementation:**
```python
import requests

class PodcastCollector:
    def __init__(self):
        self.api_key = settings.listen_notes_api_key
        self.base_url = "https://listen-api.listennotes.com/api/v2"
    
    def collect_appearances(self, industry: str, role_level: str = "VP") -> List[Dict]:
        """
        Find executives who appeared on podcasts recently
        """
        # Search for podcasts in industry
        search_response = requests.get(
            f"{self.base_url}/search",
            headers={"X-ListenAPI-Key": self.api_key},
            params={
                "q": f"{role_level} {industry}",
                "type": "episode",
                "language": "English",
                "only_in": "title,description",
                "sort_by_date": 1,
                "published_after": self._get_date_30_days_ago()
            }
        )
        
        episodes = search_response.json().get("results", [])
        
        signals = []
        for episode in episodes:
            # Get episode details
            episode_id = episode.get("id")
            episode_details = requests.get(
                f"{self.base_url}/episodes/{episode_id}",
                headers={"X-ListenAPI-Key": self.api_key}
            ).json()
            
            # Extract guest information
            guest_name = episode_details.get("title", "").split(":")[0]  # Usually format: "Guest Name: Topic"
            
            # Check transcript for "what's next" language
            transcript = self._get_transcript(episode_id)
            if self._has_movement_signals(transcript):
                signals.append({
                    "name": guest_name,
                    "source": "podcast",
                    "signal_type": "podcast_appearance",
                    "content": episode_details.get("description", ""),
                    "signal_data": {
                        "podcast_title": episode.get("podcast_title", ""),
                        "published_date": episode.get("pub_date_ms"),
                        "transcript_excerpt": transcript[:500] if transcript else ""
                    }
                })
        
        return signals
    
    def _has_movement_signals(self, transcript: str) -> bool:
        """Detect phrases indicating job movement"""
        movement_phrases = [
            "excited about what's next",
            "looking for new opportunities",
            "exploring options",
            "next chapter",
            "new challenge",
            "considering my options"
        ]
        
        transcript_lower = transcript.lower()
        return any(phrase in transcript_lower for phrase in movement_phrases)
    
    def _get_transcript(self, episode_id: str) -> str:
        """Get transcript from Listen Notes or YouTube"""
        # Listen Notes provides transcripts for some episodes
        # Or use YouTube transcript API if podcast is on YouTube
        return ""
```

**Cost:** Free tier: 10,000 requests/month, then $0.01 per request

---

### Option B: YouTube Transcripts

**For podcasts that are also on YouTube:**

```python
from youtube_transcript_api import YouTubeTranscriptApi

class PodcastCollector:
    def get_youtube_transcript(self, video_id: str) -> str:
        """Get transcript from YouTube video"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([item["text"] for item in transcript_list])
            return transcript
        except:
            return ""
```

---

## 3. Content Platform Scraping (Substack, Medium)

### Option A: RSS Feeds + Web Scraping

```python
import feedparser
import requests
from bs4 import BeautifulSoup

class ContentCollector:
    def collect_substack_signals(self, industry: str) -> List[Dict]:
        """
        Find executives writing thought leadership content
        """
        # Search Substack for industry-related newsletters
        substack_search_url = f"https://substack.com/api/v1/search/publications?q={industry}"
        
        response = requests.get(substack_search_url)
        publications = response.json().get("results", [])
        
        signals = []
        for pub in publications[:20]:  # Limit to top 20
            # Get RSS feed
            rss_url = f"{pub.get('url', '')}/feed"
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:5]:  # Recent 5 posts
                # Check if author is VP-level
                author = entry.get("author", "")
                if self._is_executive_level(author):
                    signals.append({
                        "name": author,
                        "source": "substack",
                        "signal_type": "article",
                        "content": entry.get("summary", ""),
                        "signal_data": {
                            "publication": pub.get("name", ""),
                            "published_date": entry.get("published", ""),
                            "url": entry.get("link", "")
                        }
                    })
        
        return signals
    
    def _is_executive_level(self, author_name: str) -> bool:
        """Check if author title suggests VP+ level"""
        exec_titles = ["VP", "Vice President", "C-level", "Chief", "Director", "Head of"]
        return any(title in author_name for title in exec_titles)
```

### Option B: Medium API (Limited)

```python
import requests

class ContentCollector:
    def collect_medium_signals(self, industry: str):
        # Medium RSS feeds are public
        medium_rss = f"https://medium.com/feed/tag/{industry}"
        feed = feedparser.parse(medium_rss)
        
        # Process similar to Substack
        # ...
```

---

## 4. Twitter/X Scraping

### Option A: Twitter API v2 (Official)

**Setup:**
```bash
pip install tweepy
```

**Implementation:**
```python
import tweepy

class ContentCollector:
    def __init__(self):
        self.twitter_bearer_token = settings.twitter_bearer_token
        self.client = tweepy.Client(bearer_token=self.twitter_bearer_token)
    
    def collect_twitter_signals(self, industry: str) -> List[Dict]:
        """
        Detect Twitter signals:
        - Follows to VCs, startup founders
        - Follows to competitor execs
        - Engagement with job-related content
        """
        # Search for tweets from executives in industry
        tweets = self.client.search_recent_tweets(
            query=f"{industry} (VP OR 'Vice President' OR C-level) -is:retweet",
            max_results=100,
            tweet_fields=["author_id", "created_at", "public_metrics"]
        )
        
        signals = []
        for tweet in tweets.data:
            # Get user details
            user = self.client.get_user(id=tweet.author_id)
            
            # Check if user follows VCs/startup accounts
            following = self._get_following_list(tweet.author_id)
            vc_follows = self._count_vc_follows(following)
            
            if vc_follows >= 3:  # Signal: follows multiple VCs
                signals.append({
                    "name": user.data.name,
                    "source": "twitter",
                    "signal_type": "follow",
                    "content": tweet.text,
                    "signal_data": {
                        "vc_follows": vc_follows,
                        "tweet_engagement": tweet.public_metrics,
                        "username": user.data.username
                    }
                })
        
        return signals
    
    def _get_following_list(self, user_id: str) -> List[str]:
        """Get list of accounts user follows"""
        # Note: This requires elevated access
        following = self.client.get_users_following(id=user_id, max_results=100)
        return [user.username for user in following.data]
    
    def _count_vc_follows(self, following: List[str]) -> int:
        """Count how many VCs/startup accounts user follows"""
        vc_keywords = ["vc", "venture", "capital", "startup", "founder"]
        return sum(1 for username in following 
                  if any(keyword in username.lower() for keyword in vc_keywords))
```

**Cost:** Free tier: 1,500 tweets/month, then paid plans

---

### Option B: Scraping (Unofficial - Use with Caution)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

class ContentCollector:
    def collect_twitter_signals_selenium(self, username: str):
        """Scrape Twitter using Selenium (not recommended, violates ToS)"""
        driver = webdriver.Chrome()
        driver.get(f"https://twitter.com/{username}/following")
        
        # Extract following list
        # ... (implementation)
        
        driver.quit()
```

**Warning:** This violates Twitter ToS. Use official API instead.

---

## 5. Conference Scraping

### Option A: Eventbrite API

```python
import requests

class ConferenceCollector:
    def collect_speaking_engagements(self, industry: str) -> List[Dict]:
        """
        Find executives speaking at conferences
        """
        # Search Eventbrite for industry events
        response = requests.get(
            "https://www.eventbriteapi.com/v3/events/search/",
            headers={"Authorization": f"Bearer {settings.eventbrite_token}"},
            params={
                "q": industry,
                "categories": "102",  # Business & Professional
                "start_date.range_start": self._get_date_30_days_ago(),
                "order_by": "start_asc"
            }
        )
        
        events = response.json().get("events", [])
        
        signals = []
        for event in events:
            # Get event details including speakers
            event_details = requests.get(
                f"https://www.eventbriteapi.com/v3/events/{event['id']}/",
                headers={"Authorization": f"Bearer {settings.eventbrite_token}"}
            ).json()
            
            # Extract speaker information from description
            description = event_details.get("description", {}).get("text", "")
            speakers = self._extract_speakers(description)
            
            for speaker in speakers:
                if self._is_executive_level(speaker):
                    signals.append({
                        "name": speaker,
                        "source": "conference",
                        "signal_type": "speaking",
                        "content": event_details.get("name", ""),
                        "signal_data": {
                            "event_name": event_details.get("name", ""),
                            "event_date": event_details.get("start", {}).get("local", ""),
                            "venue": event_details.get("venue", {})
                        }
                    })
        
        return signals
```

### Option B: Web Scraping Conference Websites

```python
from bs4 import BeautifulSoup
import requests

class ConferenceCollector:
    def scrape_conference_speakers(self, conference_url: str):
        """Scrape speakers from conference website"""
        response = requests.get(conference_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find speaker sections (varies by site)
        speaker_sections = soup.find_all("div", class_="speaker")  # Adjust selector
        
        speakers = []
        for section in speaker_sections:
            name = section.find("h3").text
            title = section.find("p", class_="title").text
            
            if self._is_executive_level(title):
                speakers.append({
                    "name": name,
                    "title": title,
                    "source": "conference",
                    "signal_type": "speaking"
                })
        
        return speakers
```

---

## 6. Email Enrichment

### Option A: Clay.com API

```python
import requests

class EmailEnricher:
    def __init__(self):
        self.api_key = settings.clay_api_key
        self.base_url = "https://api.clay.com/v1"
    
    def enrich_candidate(self, linkedin_url: str) -> Dict:
        """Get email and other data from LinkedIn URL"""
        response = requests.post(
            f"{self.base_url}/enrichment",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "linkedin_url": linkedin_url
            }
        )
        
        return response.json()
```

### Option B: Hunter.io

```python
import requests

class EmailEnricher:
    def find_email(self, first_name: str, last_name: str, company: str) -> str:
        """Find email using Hunter.io"""
        response = requests.get(
            "https://api.hunter.io/v2/email-finder",
            params={
                "api_key": settings.hunter_api_key,
                "first_name": first_name,
                "last_name": last_name,
                "domain": self._extract_domain(company)
            }
        )
        
        return response.json().get("data", {}).get("email", "")
```

---

## Complete Implementation Example

Here's how to wire it all together:

```python
# src/signal_fusion/collectors.py
from typing import List, Dict
from datetime import datetime, timedelta
import requests
from apify_client import ApifyClient
from src.config import settings

class SignalCollector:
    def __init__(self):
        self.linkedin = LinkedInCollector()
        self.podcast = PodcastCollector()
        self.content = ContentCollector()
        self.conference = ConferenceCollector()
    
    def collect_all_signals(
        self,
        industry: str,
        role_level: str = "VP",
        limit: int = 50
    ) -> List[Dict]:
        """Collect signals from all sources"""
        all_signals = []
        
        # Collect from each source (can run in parallel)
        try:
            linkedin_signals = self.linkedin.collect_job_change_signals(industry, role_level)
            all_signals.extend(linkedin_signals)
        except Exception as e:
            print(f"LinkedIn collection failed: {e}")
        
        try:
            podcast_signals = self.podcast.collect_appearances(industry, role_level)
            all_signals.extend(podcast_signals)
        except Exception as e:
            print(f"Podcast collection failed: {e}")
        
        # ... (other sources)
        
        # Deduplicate and limit
        return self._deduplicate_signals(all_signals, limit)
    
    def _deduplicate_signals(self, signals: List[Dict], limit: int) -> List[Dict]:
        """Remove duplicates based on LinkedIn URL or email"""
        seen = set()
        unique = []
        
        for signal in signals:
            key = signal.get("linkedin_url") or signal.get("email")
            if key and key not in seen:
                seen.add(key)
                unique.append(signal)
                if len(unique) >= limit:
                    break
        
        return unique
```

---

## Rate Limiting & Best Practices

1. **Respect Rate Limits:**
   - LinkedIn: Max 100 profiles/day (via Apify)
   - Twitter API: 300 requests/15min
   - Listen Notes: 10,000/month free tier

2. **Error Handling:**
   ```python
   try:
       signals = collector.collect()
   except RateLimitError:
       time.sleep(3600)  # Wait 1 hour
   except Exception as e:
       logger.error(f"Collection failed: {e}")
   ```

3. **Caching:**
   - Cache results to avoid duplicate API calls
   - Store in database with timestamps

4. **Legal Compliance:**
   - Use official APIs when available
   - Respect robots.txt
   - Follow ToS for each platform
   - Consider GDPR/privacy implications

---

## Next Steps

1. **Choose your tools:**
   - LinkedIn: Apify (recommended) or PhantomBuster
   - Podcasts: Listen Notes API
   - Content: RSS feeds + BeautifulSoup
   - Twitter: Official API v2
   - Conferences: Eventbrite API or web scraping

2. **Get API keys:**
   - Sign up for Apify, Listen Notes, Twitter API, etc.
   - Add keys to `.env` file

3. **Implement collectors:**
   - Replace stub functions in `src/signal_fusion/collectors.py`
   - Test each collector individually
   - Add error handling and logging

4. **Test:**
   ```bash
   python -c "from src.signal_fusion.collectors import SignalCollector; sc = SignalCollector(); print(sc.collect_all_signals('fintech', 'VP', 10))"
   ```

---

## Cost Estimates

- **Apify LinkedIn:** ~$0.10-0.50 per 100 profiles
- **Listen Notes:** Free tier (10K/month) or $0.01/request
- **Twitter API:** Free tier (1.5K tweets/month) or $100/month
- **Eventbrite:** Free tier available
- **Total MVP cost:** ~$50-200/month for moderate usage

