"""Wikipedia summary tool."""
import urllib.parse
import requests
import traceback
from typing import Optional

from src.studypilot.config import logger

def wikipedia_summary(topic: str) -> str:
    """Get a summary of a topic from Wikipedia."""
    try:
        encoded_topic = urllib.parse.quote(topic)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_topic}"
        headers = {"User-Agent": "StudyPilot/1.0"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return f"Note: No dedicated Wikipedia article was found for '{topic}'. The agent should proceed using its own extensive knowledge base or other search tools to answer."
            
        response.raise_for_status()
        data = response.json()
        
        extract = data.get("extract", "")
        if not extract:
            return f"Note: No summary available on Wikipedia for '{topic}'. The agent should proceed using its own extensive knowledge base to answer."
            
        # Truncate to 3000 chars if necessary
        return extract[:3000] + ("..." if len(extract) > 3000 else "")
        
    except Exception as e:
        logger.warning(f"Wikipedia summary lookup note for '{topic}': {e}")
        return f"Note: Wikipedia is currently unreachable for '{topic}'. The agent should proceed using its own extensive knowledge base or web search to answer."
