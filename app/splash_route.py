
""" Shared renderer for the application's splash page.
    ToDo: V2 will need new pages to display P4 data and results, and to allow user to
      select and run P4 analysis.
      Will this be a template or need unique page for each analysis? 
        For now, just a splash page to show the app is running.
    """

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def render_splash(
    request: Request,
    *,
    splash_screen: str,
    app_name: str,
    version: str,
    startup_iso: object,
    uptime_seconds: float,
    db_router_enabled: bool,
):
    """Render the shared splash template with application runtime values."""
    return templates.TemplateResponse(
        request=request,
        name="splash.html",
        context={
            "splash_screen": splash_screen,
            "app_name": app_name,
            "version": version,
            "startup_iso": startup_iso,
            "uptime_seconds": uptime_seconds,
            "db_router_enabled": db_router_enabled,
        },
    )
