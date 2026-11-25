"""Extract Indicators of Compromise (IOCs) from threat report text.

Pulls out IP addresses, domain names, URLs, and file hashes (MD5, SHA1,
SHA256) using regex. Designed for plain-English threat reports, not raw
log data.

Defanged indicators (e.g. hxxp://, 192.168.1[.]1, example[.]com) are
re-fanged before returning so the caller gets usable values.

Usage:
    from export.ioc_extract import extract_iocs
    iocs = extract_iocs("The malware called home to 10.0.0.5 on port 443.")
    # {"ipv4": ["10.0.0.5"], "domains": [], "urls": [], "hashes": []}
"""
import re

# ---------------------------------------------------------------------------
# Defang helpers
# ---------------------------------------------------------------------------

def _refang(text):
    """Convert defanged indicators back to their real form."""
    t = text
    t = t.replace("hxxp://", "http://").replace("hxxps://", "https://")
    t = t.replace("hXXp://", "http://").replace("hXXps://", "https://")
    t = re.sub(r"\[\.\]", ".", t)
    t = re.sub(r"\[dot\]", ".", t, flags=re.IGNORECASE)
    t = t.replace("[:]", ":")
    return t


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_IPV4 = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(?:\[?\.\]?)"  # allow defanged dots
    r"){3}"
    r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b"
)

_MD5 = re.compile(r"\b[0-9a-fA-F]{32}\b")
_SHA1 = re.compile(r"\b[0-9a-fA-F]{40}\b")
_SHA256 = re.compile(r"\b[0-9a-fA-F]{64}\b")

_URL = re.compile(
    r"(?:hxxps?|https?|ftp)(?:\[:\]|:)//"
    r"[^\s\"'<>\]\)]{4,}",
    re.IGNORECASE,
)

_DOMAIN = re.compile(
    r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
    r"(?:\[?\.\]?)"  # allow defanged dots
    r")+"
    r"(?:com|net|org|io|xyz|info|ru|cn|de|uk|top|biz|cc|pw|tk)\b",
    re.IGNORECASE,
)

# Common false-positive patterns to exclude
_FP_DOMAINS = {
    "microsoft.com", "windows.com", "google.com", "github.com",
    "attack.mitre.org", "schemas.microsoft.com",
}

_FP_IP_PREFIXES = ("0.", "127.", "255.")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_iocs(text):
    """Extract IOCs from raw threat report text.

    Returns a dict with four keys:
        ipv4:    list of IPv4 addresses (strings, deduplicated)
        domains: list of domain names (strings, deduplicated)
        urls:    list of URLs (strings, deduplicated)
        hashes:  list of dicts: {"value": "abc...", "type": "md5"|"sha1"|"sha256"}
    """
    cleaned = _refang(text)

    # IPv4
    raw_ips = _IPV4.findall(cleaned)
    ips = []
    seen_ips = set()
    for ip in raw_ips:
        ip = ip.replace("[.]", ".").replace("[", "").replace("]", "")
        if ip in seen_ips:
            continue
        if any(ip.startswith(p) for p in _FP_IP_PREFIXES):
            continue
        seen_ips.add(ip)
        ips.append(ip)

    # URLs (before domains, so we can exclude domain-only matches)
    raw_urls = _URL.findall(cleaned)
    urls = []
    seen_urls = set()
    url_domains = set()
    for u in raw_urls:
        u = u.rstrip(".,;:)\"'")
        if u in seen_urls:
            continue
        seen_urls.add(u)
        urls.append(u)
        # Extract domain from URL to skip it in domain list
        m = re.match(r"https?://([^/:]+)", u, re.IGNORECASE)
        if m:
            url_domains.add(m.group(1).lower())

    # Domains
    raw_domains = _DOMAIN.findall(cleaned)
    domains = []
    seen_domains = set()
    for d in raw_domains:
        d = d.replace("[.]", ".").replace("[", "").replace("]", "").lower()
        if d in seen_domains or d in _FP_DOMAINS or d in url_domains:
            continue
        seen_domains.add(d)
        domains.append(d)

    # Hashes (longest first to avoid substring matches)
    hashes = []
    seen_hashes = set()

    for h in _SHA256.findall(cleaned):
        h_lower = h.lower()
        if h_lower not in seen_hashes:
            seen_hashes.add(h_lower)
            hashes.append({"value": h_lower, "type": "sha256"})

    for h in _SHA1.findall(cleaned):
        h_lower = h.lower()
        if h_lower not in seen_hashes and not any(
            h_lower in existing["value"] for existing in hashes
        ):
            seen_hashes.add(h_lower)
            hashes.append({"value": h_lower, "type": "sha1"})

    for h in _MD5.findall(cleaned):
        h_lower = h.lower()
        if h_lower not in seen_hashes and not any(
            h_lower in existing["value"] for existing in hashes
        ):
            seen_hashes.add(h_lower)
            hashes.append({"value": h_lower, "type": "md5"})

    return {
        "ipv4": ips,
        "domains": domains,
        "urls": urls,
        "hashes": hashes,
    }


def has_iocs(ioc_result):
    """Return True if the extraction found at least one IOC."""
    return bool(
        ioc_result["ipv4"]
        or ioc_result["domains"]
        or ioc_result["urls"]
        or ioc_result["hashes"]
    )
