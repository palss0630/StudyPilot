"""Webpage reader tool with SSRF protection."""
import socket
import urllib.parse
import ipaddress
import requests
import traceback
from bs4 import BeautifulSoup
from typing import Optional

from src.studypilot.config import logger

def is_private_ip(ip_str: str) -> bool:
    """Check if an IP string is private/loopback/etc."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_reserved or str(ip) in ("0.0.0.0", "::")
    except ValueError:
        return False

def check_ssrf(url: str) -> None:
    """Validate URL to prevent Server-Side Request Forgery."""
    parsed = urllib.parse.urlparse(url)
    
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only http/https are allowed.")
        
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: Missing hostname.")
        
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for res in addr_info:
            ip = res[4][0]
            if is_private_ip(ip):
                raise ValueError(f"SSRF Protection: Hostname resolves to private/internal IP ({ip}).")
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {hostname}")

def read_webpage(url: str) -> str:
    """Safely fetch and extract text from a webpage."""
    try:
        check_ssrf(url)
        
        headers = {"User-Agent": "StudyPilot/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        
        # Truncate to 4000 characters
        if len(text) > 4000:
            text = text[:4000] + "\n...[TRUNCATED]"
            
        return text
    except Exception as e:
        logger.error(f"Error reading webpage {url}: {e}\n{traceback.format_exc()}")
        return f"Error reading webpage: {e}"
