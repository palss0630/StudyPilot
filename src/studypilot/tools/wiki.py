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
            return f"No Wikipedia article found for: {topic}"
            
        response.raise_for_status()
        data = response.json()
        
        extract = data.get("extract", "")
        if not extract:
            return f"No summary available for: {topic}"
            
        # Truncate to 3000 chars if necessary
        return extract[:3000] + ("..." if len(extract) > 3000 else "")
        
    except Exception as e:
        logger.error(f"Error fetching Wikipedia summary: {e}\n{traceback.format_exc()}")
        return f"Error fetching Wikipedia summary: {e}"
