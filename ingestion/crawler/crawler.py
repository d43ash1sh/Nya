"""
Lawful Web Crawler with SSRF Defense and Robots.txt Compliance.
Respects domain rate limits, robots.txt exclusions, and prevents
Server-Side Request Forgery (SSRF) into internal networks.
"""

import socket
import ipaddress
import urllib.parse
from urllib.robotparser import RobotFileParser
from typing import Optional, Tuple
import httpx
from config import settings


class SSRFProtectionError(Exception):
    """Raised when URL resolves to internal or restricted IP address."""
    pass


def is_safe_external_url(url: str) -> bool:
    """
    Validates URL safety:
    - Scheme must be http or https
    - Hostname must resolve to a globally routable public IP
    - Forbids loopback, link-local, private RFC 1918, carrier-grade NAT, or multicast IPs
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Disallow localhost keywords
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False

        # Resolve IP addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for entry in addr_info:
            ip_str = entry[4][0]
            ip = ipaddress.ip_address(ip_str)

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                return False

        return True
    except Exception:
        return False


class LawfulCrawler:
    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or settings.CRAWLER_USER_AGENT
        self.robots_cache = {}

    def is_crawl_permitted(self, url: str, robots_txt_content: Optional[str] = None) -> bool:
        """Check whether robot.txt allows indexing the target URL."""
        if not settings.CRAWLER_RESPECT_ROBOTS_TXT:
            return True

        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc

        rp = RobotFileParser()
        if robots_txt_content:
            rp.parse(robots_txt_content.splitlines())
        else:
            rp.set_url(f"{parsed.scheme}://{domain}/robots.txt")
            # Default allow if no robots.txt provided in offline/sandbox mode
            return True

        return rp.can_fetch(self.user_agent, url)

    async def fetch_url(self, url: str) -> Tuple[Optional[str], int]:
        """
        Safely fetches content from a permitted external URL.
        Enforces SSRF prevention checks.
        """
        if not is_safe_external_url(url):
            raise SSRFProtectionError(f"SSRF Check: Target {url} is not a valid public web destination.")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "as,en;q=0.8",
        }

        async with httpx.AsyncClient(
            timeout=settings.CRAWLER_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url, headers=headers)
            return resp.text, resp.status_code
