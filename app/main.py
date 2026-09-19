""" Application: PPPPdev    (P4)
    File: app/main.py  
    
    This is the main entry point for the P4 FastAPI application.
    It sets up the application, including the database connection,
    CORS middleware, and API routes.
    The Database [to be] used is PostgreSQL, accessed asynchronously via SQLAlchemy 2.
    The application uses an async lifespan context manager to handle startup 
    and shutdown events, such as creating database tables and disposing of 
    the connection pool.  
    The API includes a health check endpoint and routes for managing users.

    Developer: Rudy J. (rudy2058@gmail.com)

    Develoment mode: 1 for now.
    
    - Data Base connections using  SQLAlchemy : Debug in process 
  - 0: No DB, testing and development mode
  - 1: SQLite database  - testing and development mode
  - 2: PostgreSQL (server must be running and ready)

    Requiments: PostgreSQL must be running for full production mode. 
        The application uses asynchronous database connections via SQLAlchemy 2, FastAPI

      To run the app. first time, follow these steps:
      1.  Check if a virtual environment is active, if not, create one and activate it by:
            - On Windows: `python -m venv venv` and `venv\Scripts\activate`
            - On macOS/Linux: `python3 -m venv venv` and `source venv/bin/activate`

      2. If runing with DB: check if PostgreSQL is tunning and user: ppp_user  -
        - . DB init in process - need first time init logic
      3. To run or restart the app, follow these steps:
         -  Run the app in this folder: v1/app/ using the command:
         - `uvicorn app.main:app --reload`
         -  Access API docs at http://localhost:8000/docs  
      
    """



from contextlib import asynccontextmanager
from datetime import datetime
import os
import select
import sys
import threading
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# importing SETTTINGS sets environment variables and reads .env file if present
from app.core.config import settings 
from app.db.database import engine, Base
from app.routers import users
from app.splash_route import render_splash

from app.utils import ppp_utils

# Splash screen or banner for the application
SPLASH_SCREEN = "Public Policy and Personality Profile tool"

# Track startup time for house keeping - use fixed-point time format to keep it simple
startup_time = None

# 0: No DB, testing and development mode; 1: SQLite; 2: PostgreSQL
DB_INIT = int(settings.DB_INIT)
print(f"*** DB_INIT value: {DB_INIT} ***")  # debug

DB_ROUTER_ENABLED = DB_INIT != 0
DB_INIT_ERROR = None

# Debug and Dev command loop for testing and development purposes
command_loop_stop = threading.Event()


def command_loop(stop_event: threading.Event) -> None:
    print("*** Command loop started. Type a command and press Enter. ***\n")
    while not stop_event.is_set():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\r{timestamp} - Enter command: ", end="", flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], 1.0)
        if ready:
            line = sys.stdin.readline()
            if not line:
                break
            command = line.strip()
            if command.lower() == "exit":
                print("\n*** Exit command received. Stopping command loop. ***")
                stop_event.set()
                break
            elif command.lower() == "q":
               # Send SIGQUIT signal to the current process to trigger a graceful shutdown
                print("\n*** Quit command received. Send SIGQUIT to Server. ***")
                app.post("/shutdown")  # Trigger shutdown endpoint
                stop_event.set()
                break
            else:            
                print(f"\nYou entered: {command} - doing nothing ")
    print("\n*** Command loop stopped. ***")
    exit(0)  # Exit the command loop thread gracefully

# Here is where the action starts. 
# The FastAPI app is created, CORS middleware is added, and the lifespan
# context manager is defined to handle startup and shutdown events. 
# The command loop runs in a separate thread for development purposes,
#  allowing the developer to enter commands while the app is running.

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.perf_counter() # use fixed-point time format to keep it simple
    print(f"*** App startup at {startup_time:.2f}") # debug

    # Get platform and System we are running on. 
    user_agent: str = f"Startup/1.0 ({sys.platform})"
   #  print(" Platform and Browser Info: ", ppp_utils.get_browser_info(user_agent ) ) # dev log  # fix later

    if DB_INIT:
        try:
            # Startup — create tables (use Alembic in production)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("*** Database initialized successfully ***")
        except Exception as exc:  # pragma: no cover - app should continue in degraded mode
            global DB_INIT_ERROR, DB_ROUTER_ENABLED
            DB_INIT_ERROR = exc
            DB_ROUTER_ENABLED = False
            print(f"*** Database initialization failed: {exc} ***")
            print("*** Continuing without DB routes because the app should not fail startup. ***")
    else:
        print("*** DB initialization skipped because DB_INIT=0 ***")

    command_thread = threading.Thread(target=command_loop, args=(command_loop_stop,), daemon=True)
    command_thread.start()  # start the command loop in a separate thread for development purposes

    yield  # and this startup code waits here for the app to run. 
    # The lifespan context manager will resume here when the app is shutting down.

    # normal shutdown processes
    
    command_loop_stop.set()
    command_thread.join(timeout=1.0)

    if DB_INIT:
        # Shutdown — dispose connection pool
        await engine.dispose()
    print("*** Server Exited ***")
  # And all done.  

# Create the FastAPI app instance with the defined lifespan context manager.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Database CRUD API — Users  |  Python 3 + FastAPI + SQLAlchemy 2",
    lifespan=lifespan,  # What signals are available for graceful shutdown?
      #   SIGINT, SIGTERM, SIGQUIT, SIGHUP, SIGUSR1, SIGUSR2
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("static/favicon.ico")

# adding a middleware to set a cookie named "connected_token" 
# with a timestamp value for each HTTP request.
# Why use a middleware for a cookie? Is there a direct way? TBD for now.
@app.middleware("http")
async def connected_cookie_middleware(request: Request, call_next):
    response = await call_next(request)
    token = f"connected:{datetime.timestamp(datetime.now( ))}"
    response.set_cookie(
        key="connected_token",
        value=token,
        httponly=False,
        samesite="lax",
        max_age=120,
    )
    return response

if DB_ROUTER_ENABLED:
    app.include_router(users.router, prefix="/api/v1")  # check this
else:
    print("*** Users CRUD routes disabled because DB_ROUTER_ENABLED=0 ***")

# handle the inital splash screen and health check endpoints.
# ToDo: add a shutdown endpoint for graceful shutdown from the command loop.
@app.get("/", response_class=HTMLResponse, tags=["meta"])
async def splash_screen(request: Request):
    """Splash screen with application startup info."""
    uptime_seconds = ( time.perf_counter() - startup_time ) if startup_time else 0 # The GitHub ChatBot likes to put in saferty checks.
    startup_iso = startup_time if startup_time else "Unknown"
    return render_splash(
        request,
        splash_screen=SPLASH_SCREEN,
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        startup_iso=startup_iso,
        uptime_seconds=uptime_seconds,
        db_router_enabled=DB_ROUTER_ENABLED,
    )

# Health check endpoint to verify the application is running and the database connection status.
# The health check endpoint returns a JSON response with the application status, version, database connection status, and any database initialization errors.
# handles Event
@app.get("/health", tags=["meta"])
async def health():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "connected": DB_ROUTER_ENABLED and DB_INIT_ERROR is None,
        "db_init": DB_INIT,
        "db_ready": DB_ROUTER_ENABLED and DB_INIT_ERROR is None,
        "db_error": str(DB_INIT_ERROR) if DB_INIT_ERROR else None,
        "connected_at": f"connected:{datetime.timestamp(datetime.now())}"
    }
# end 
