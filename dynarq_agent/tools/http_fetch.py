"""An HTTP fetch tool that returns readable page text, with an SSRF guard.

Letting an agent fetch URLs is powerful, and a classic way to abuse it is
server-side request forgery: pointing it at http://localhost or a cloud
metadata address (169.254.169.254) to reach things the agent should not. This
tool only allows http(s), resolves the host, and refuses private, loopback,
link-local and reserved addresses, re-checking on every redirect.
"""
import html
import ipaddress
import re
import socket
import urllib.error
import urllib.parse
import urllib.request

from ..tool import Tool

MAX_BYTES = 500_000
DEFAULT_MAX_CHARS = 4000

_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
_TAG = re.compile(r"<[^>]+>")


def _host_is_public(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False
    return True


def _validate(url: str):
    parts = urllib.parse.urlparse(url)
    if parts.scheme not in ("http", "https"):
        return "Error: only http and https URLs are allowed"
    if not parts.hostname:
        return "Error: URL has no host"
    if not _host_is_public(parts.hostname):
        return "Error: refusing to fetch a private, loopback or reserved address"
    return None


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Re-validate the target of every redirect so it cannot hop to a private host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if _validate(newurl):
            raise urllib.error.HTTPError(newurl, code, "blocked redirect to a disallowed host", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _html_to_text(raw: str) -> str:
    raw = _SCRIPT.sub(" ", raw)
    raw = _TAG.sub(" ", raw)
    return html.unescape(raw)


def fetch_url(url: str, max_chars: int = DEFAULT_MAX_CHARS, timeout: int = 15) -> str:
    error = _validate(url)
    if error:
        return error

    opener = urllib.request.build_opener(_SafeRedirect())
    request = urllib.request.Request(url, headers={"User-Agent": "dynarq-agent/1.0"})
    try:
        with opener.open(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(MAX_BYTES + 1)
    except Exception as exc:  # noqa: BLE001 - report any network/parse issue back to the agent
        return f"Error: {exc}"

    text = raw[:MAX_BYTES].decode("utf-8", errors="replace")
    if "html" in content_type.lower() or "<html" in text[:2000].lower():
        text = _html_to_text(text)
    text = " ".join(text.split())

    if len(text) > max_chars:
        return text[:max_chars].rstrip() + f"\n... [truncated at {max_chars} characters]"
    return text or "(empty response)"


FETCH_URL = Tool(
    name="fetch_url",
    description="Fetch an http(s) web page and return its readable text (HTML tags stripped).",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "the http or https URL to fetch"},
            "max_chars": {"type": "integer", "description": "maximum characters to return (default 4000)"},
        },
        "required": ["url"],
    },
    func=fetch_url,
)
