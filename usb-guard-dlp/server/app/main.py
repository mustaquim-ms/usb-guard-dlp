from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

from server.app.database import engine, Base
from server.app import models
from server.app.routes import api_agent, api_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Octate Odyssey Device Block Service")

# MOUNT STATIC FILES (For Logo and CSS)
# Ensure your logo is at: server/static/logo.webp
app.mount("/static", StaticFiles(directory="server/static"), name="static")

app.include_router(api_agent.router)
app.include_router(api_admin.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

@app.get("/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})