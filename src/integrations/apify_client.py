"""Apify client for LinkedIn scraping"""

from apify_client import ApifyClient
from typing import List, Dict
from src.config import settings


class ApifyLinkedInScraper:
    """Wrapper for Apify LinkedIn Profile Scraper"""
    
    def __init__(self):
        if not settings.apify_api_token:
            raise ValueError("APIFY_API_TOKEN not set in environment")
        self.client = ApifyClient(settings.apify_api_token)
    
    def search_profiles(
        self,
        search_query: str,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Search LinkedIn profiles using Apify
        
        Args:
            search_query: LinkedIn search query (e.g., "VP Engineering fintech")
            max_results: Maximum number of profiles to return
        
        Returns:
            List of profile dictionaries
        """
        # Run Apify actor
        run_input = {
            "startUrls": [
                {
                    "url": f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
                }
            ],
            "maxItems": max_results,
        }
        
        print(f"Starting Apify LinkedIn scraper for: {search_query}")
        run = self.client.actor("apify/linkedin-profile-scraper").call(
            run_input=run_input
        )
        
        # Wait for completion
        print("Waiting for scraper to finish...")
        self.client.run(run["defaultDatasetId"]).wait_for_finish()
        
        # Get results
        print("Fetching results...")
        dataset = self.client.dataset(run["defaultDatasetId"])
        items = dataset.list_items()
        
        profiles = []
        for item in items.get("items", []):
            profiles.append({
                "name": item.get("fullName", ""),
                "linkedin_url": item.get("url", ""),
                "current_title": item.get("headline", ""),
                "current_company": self._extract_company(item),
                "location": item.get("location", ""),
                "summary": item.get("summary", ""),
                "experience": item.get("experiences", []),
                "connections_count": item.get("connectionsCount", 0),
                "recent_activity": item.get("recentActivity", [])
            })
        
        print(f"Found {len(profiles)} profiles")
        return profiles
    
    def _extract_company(self, profile_data: Dict) -> str:
        """Extract current company from profile data"""
        experiences = profile_data.get("experiences", [])
        if experiences:
            # Get most recent experience
            current_exp = experiences[0]
            return current_exp.get("companyName", "")
        return ""


# Example usage:
if __name__ == "__main__":
    scraper = ApifyLinkedInScraper()
    profiles = scraper.search_profiles("VP Engineering fintech", max_results=10)
    for profile in profiles:
        print(f"{profile['name']} - {profile['current_title']} @ {profile['current_company']}")

