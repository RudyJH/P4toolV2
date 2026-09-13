""" Utility functions for parsing user agents and extracting browser and platform information.
    Should this be a class or just a module with functions? TBD. For now, it's a module with functions.
"""

__package__ = "ppp_utils"

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse

def parse_browser(user_agent: str) -> str:
    ua = user_agent or ""
    if "OPR" in ua or "Opera" in ua:
        return "Opera"
    if "Edg" in ua or "Edge" in ua:
        return "Edge"
    if "Chrome" in ua and "Safari" in ua:
        return "Chrome"
    if "Safari" in ua and "Chrome" not in ua:
        return "Safari"
    if "Firefox" in ua:
        return "Firefox"
    if "MSIE" in ua or "Trident" in ua:
        return "Internet Explorer"
    return "Unknown"


def parse_platform(user_agent: str) -> str:
    ua = user_agent or ""
    if "Windows" in ua:
        return "Windows"
    if "Macintosh" in ua or "Mac OS X" in ua:
        return "macOS"
    if "Linux" in ua and "Android" not in ua:
        return "Linux"
    if "Android" in ua:
        return "Android"
    if "iPhone" in ua or "iPad" in ua or "iPod" in ua:
        return "iOS"
    return "Unknown"


""" how to use:
 # Get browser info at startup for logging purposes. Haha! that only makes on the client
    fake_headers = {"user-agent": "Startup/1.0"}
    class _DummyRequest:
        def __init__(self, headers):
            self.headers = headers
    info = ppp_utils.get_browser_info(_DummyRequest(fake_headers))
    print("Startup browser info helper ready:", info)
    """

""" def get_browser_info(request: Request) -> dict:
    user_agent = request.headers.get("user-agent")
    return {
        "user_agent": user_agent,
        "browser": parse_browser(user_agent),
        "platform": parse_platform(user_agent),
    }

""" 