"""Listen Notes API client for podcast scraping"""

import requests
from typing import List, Dict
from datetime import datetime, timedelta
from src.config import settings


class ListenNotesClient:
    """Client for Listen Notes API to find podcast appearances"""
    
    def __init__(self):
        if not settings.listen_notes_api_key:
            raise ValueError("LISTEN_NOTES_API_KEY not set in environment")
        self.api_key = settings.listen_notes_api_key
        self.base_url = "https://listen-api.listennotes.com/api/v2"
        self.headers = {"X-ListenAPI-Key": self.api_key}
    
    def search_episodes(
        self,
        query: str,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Search for podcast episodes
        
        Args:
            query: Search query (e.g., "VP Engineering fintech")
            max_results: Maximum episodes to return
        
        Returns:
            List of episode dictionaries
        """
        episodes = []
        page = 1
        
        while len(episodes) < max_results:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={
                    "q": query,
                    "type": "episode",
                    "language": "English",
                    "sort_by_date": 1,
                    "published_after": self._get_date_30_days_ago(),
                    "offset": (page - 1) * 10,
                    "limit": min(10, max_results - len(episodes))
                }
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break
            
            for episode in results:
                episodes.append({
                    "id": episode.get("id", ""),
                    "title": episode.get("title", ""),
                    "description": episode.get("description", ""),
                    "podcast_title": episode.get("podcast_title", ""),
                    "published_date": episode.get("pub_date_ms", 0),
                    "audio_url": episode.get("audio", ""),
                    "guest_name": self._extract_guest_name(episode.get("title", "")),
                    "transcript": None  # Would need to fetch separately
                })
            
            page += 1
            
            # Rate limiting: free tier allows 10,000 requests/month
            if page > 10:  # Safety limit
                break
        
        return episodes[:max_results]
    
    def get_episode_details(self, episode_id: str) -> Dict:
        """Get detailed episode information"""
        response = requests.get(
            f"{self.base_url}/episodes/{episode_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return {}
    
    def _extract_guest_name(self, title: str) -> str:
        """Extract guest name from episode title"""
        # Common formats:
        # "Guest Name: Topic"
        # "Topic with Guest Name"
        # "Guest Name on Topic"
        
        if ":" in title:
            return title.split(":")[0].strip()
        elif " with " in title:
            parts = title.split(" with ")
            if len(parts) > 1:
                return parts[1].split(" on ")[0].strip()
        elif " on " in title:
            parts = title.split(" on ")
            if len(parts) > 1:
                return parts[0].strip()
        
        return title.split()[0]  # Fallback: first word
    
    def _get_date_30_days_ago(self) -> int:
        """Get timestamp for 30 days ago (in milliseconds)"""
        date_30_days_ago = datetime.now() - timedelta(days=30)
        return int(date_30_days_ago.timestamp() * 1000)


# Example usage:
if __name__ == "__main__":
    client = ListenNotesClient()
    episodes = client.search_episodes("VP Engineering", max_results=10)
    for episode in episodes:
        print(f"{episode['guest_name']} - {episode['title']}")

