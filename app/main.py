from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import init_db
from fastapi import Depends, HTTPException,BackgroundTasks
from app.utils import generate_short_code
from app.crud import create_link,delete_link,increment_clicks,get_link,purge_expired_links,get_all_active_links
from app.database import get_db
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from fastapi.responses import RedirectResponse,HTMLResponse
from pydantic import field_validator
from app.templates import GHOST_PAGE
import os


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

BANNER = """
  ____ _               _   _     _       _      
 / ___| |__   ___  ___| |_| |   (_)_ __ | | __ 
| |  _| '_ \ / _ \/ __| __| |   | | '_ \| |/ / 
| |_| | | | | (_) \__ \ |_| |___| | | | |   <  
 \____|_| |_|\___/|___/\__\_____|_|_| |_|_|\_\\
      -- Self-Destructing URL Shortener --
"""
#initialize db
init_db()
print(BANNER)

app=FastAPI(title="GhostLink")

class LinkCreate(BaseModel):
    long_url: str  
    max_clicks: int = 1
    ttl_hours: int = 24
    custom_code: str = None
    @field_validator('max_clicks')
    def limit_clicks(cls, v):
        if v > 500: # max click limit
            raise ValueError('Maximum clicks allowed is 500.')
        return v
    @field_validator('ttl_hours')
    def limit_ttl(cls, v):
        if v > 168: # (1 week)
            raise ValueError('Maximum TTL is 168 hours (7 days).')
        return v
    
    @field_validator('long_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        base = os.getenv("BASE_URL", "localhost")
        if base in v:
            raise ValueError("Cannot shorten a GhostLink URL.")
        return v
    
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/shorten")
def shorten_url(payload: LinkCreate):
   
    with get_db() as conn:
        
        short_code = payload.custom_code if payload.custom_code else generate_short_code()
        
        print(f"DEBUG: Created ghost link {short_code} for {payload.long_url}")
        
        if get_link(conn, short_code):
            raise HTTPException(status_code=400, detail="Short code already in use.")
            
        try:
            create_link(
                conn, 
                payload.long_url, 
                payload.max_clicks, 
                payload.ttl_hours, 
                short_code
            )
            return {"short_url": f"{BASE_URL}/{short_code}", "short_code": short_code}
        except Exception:
            raise HTTPException(status_code=500, detail="Could not create link.")
        
@app.get("/{short_code}")
def redirect_to_url(short_code: str,background_tasks: BackgroundTasks):
    
    with get_db() as conn:
        link = get_link(conn, short_code)
        
        
        if not link:
            return HTMLResponse(content=GHOST_PAGE, status_code=404)
        print(f"DEBUG: Redirecting {short_code} to {link['long_url']}")

        background_tasks.add_task(purge_expired_links, conn)

        expires_at = datetime.strptime(link['expires_at'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() > expires_at:
            delete_link(conn, short_code)
            raise HTTPException(status_code=404, detail="Link has vanished.")
        
        new_clicks = link['current_clicks'] + 1
        
        if new_clicks >= link['max_clicks']:
            delete_link(conn, short_code)
        else:
            increment_clicks(conn, short_code)
            
        return RedirectResponse(url=link['long_url'])
    
@app.get("/stats/{short_code}")
def get_link_stats(short_code: str):
    with get_db() as conn:
        link = get_link(conn, short_code)
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found.")
            
        return {
            "short_code": link["short_code"],
            "long_url": link["long_url"],
            "clicks_remaining": link["max_clicks"] - link["current_clicks"],
            "expires_at": link["expires_at"]
        }
    
@app.delete("/cleanup")
def cleanup_expired():
    with get_db() as conn:
        deleted_count = purge_expired_links(conn)
    return {"message": f"Ghosted {deleted_count} expired links."}

@app.get("/debug/all")
def get_dashboard():
    with get_db() as conn:
        links = get_all_active_links(conn)
        return [dict(link) for link in links]
    
@app.post("/ghost/{short_code}")
def force_expire(short_code: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE links SET expires_at = CURRENT_TIMESTAMP WHERE short_code = ?",
            (short_code,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Link not found.")
            
    print(f"DEBUG: Manually expired {short_code}")
    return {"message": f"Link {short_code} has been ghosted."}

@app.patch("/revive/{short_code}")
def extend_link(short_code: str, hours: int = 24):
    with get_db() as conn:
        link = get_link(conn, short_code)
        if not link:
            raise HTTPException(status_code=404, detail="Link not found.")
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE links SET expires_at = datetime(expires_at, '+' || ? || ' hours') WHERE short_code = ?",
            (hours, short_code)
        )
        conn.commit()
        
    return {"message": f"Link {short_code} extended by {hours} hours."}

@app.delete("/{short_code}")
def manual_delete(short_code: str):
    """Allows manual destruction of a ghost link."""
    with get_db() as conn:
        link = get_link(conn, short_code)
        if not link:
            raise HTTPException(status_code=404, detail="Link not found.")
        
        delete_link(conn, short_code)
        print(f"DEBUG: Manually ghosted {short_code}")
        
    return {"message": f"Link {short_code} has been returned to the void."}