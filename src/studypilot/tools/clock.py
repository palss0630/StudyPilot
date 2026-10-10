"""Clock tool."""
import time
from datetime import datetime
import traceback

from src.studypilot.config import logger

def current_datetime() -> str:
    """Get the current date and time in a readable format."""
    try:
        now = datetime.now()
        local_timezone = time.tzname[time.daylight]
        formatted = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
        return f"Current Date and Time: {formatted} {local_timezone}"
    except Exception as e:
        logger.error(f"Error getting datetime: {e}\n{traceback.format_exc()}")
        return f"Error getting current datetime: {e}"
