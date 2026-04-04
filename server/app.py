# server/app.py
# ──────────────────────────────────────────────────────────────
# This file starts the web server for your environment.
#
# create_fastapi_app() takes your Environment class and
# automatically creates these HTTP endpoints:
#   POST /reset  → calls environment.reset()
#   POST /step   → calls environment.step()
#   GET  /state  → calls environment.state
#
# That's it. One line does all of that.
# ──────────────────────────────────────────────────────────────

from openenv.core.env_server import create_fastapi_app
from server.environment import MumbaiLastMileEnvironment
from models import MumbaiAction, MumbaiObservation

# This creates the "app" object — uvicorn (the web server) will use this
app = create_fastapi_app(
    MumbaiLastMileEnvironment,
    action_cls=MumbaiAction,
    observation_cls=MumbaiObservation,
)