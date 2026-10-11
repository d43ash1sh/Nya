"""
Security and SSRF Protection Unit Tests.
Verifies that crawler rejects private/internal IPs, localhost, link-local addresses,
and malicious URL schemes.
"""

import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "search-api"))
sys.path.insert(0, str(root_dir))

from ingestion.crawler.crawler import is_safe_external_url, LawfulCrawler, SSRFProtectionError


def test_ssrf_blocks_localhost():
    assert is_safe_external_url("http://localhost:8000") is False
    assert is_safe_external_url("http://127.0.0.1:8000") is False
    assert is_safe_external_url("http://127.0.0.1/admin") is False


def test_ssrf_blocks_private_rfc1918():
    assert is_safe_external_url("http://10.0.0.1/secrets") is False
    assert is_safe_external_url("http://192.168.1.1/router") is False
    assert is_safe_external_url("http://172.16.0.1/") is False


def test_ssrf_blocks_cloud_metadata():
    # AWS/GCP cloud metadata IP: 169.254.169.254
    assert is_safe_external_url("http://169.254.169.254/latest/meta-data/") is False


def test_ssrf_blocks_non_http_schemes():
    assert is_safe_external_url("file:///etc/passwd") is False
    assert is_safe_external_url("gopher://127.0.0.1:70") is False
    assert is_safe_external_url("ftp://example.com/file") is False


@pytest.mark.asyncio
async def test_crawler_raises_on_ssrf():
    crawler = LawfulCrawler()
    with pytest.raises(SSRFProtectionError):
        await crawler.fetch_url("http://127.0.0.1:8000/internal")
