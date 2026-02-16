from fastapi import FastAPI
from app.database import init_db
from fastapi import Depends, HTTPException
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

#initialize db
init_db()

app=FastAPI(title="GhostLink")

class LinkCreate(BaseModel):
    long_url: str  
    max_clicks: int = 1
    ttl_hours: int = 24
    custom_code: str = None

    @field_validator('long_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        base = os.getenv("BASE_URL", "localhost")
        if base in v:
            raise ValueError("Cannot shorten a GhostLink URL.")
        return v
    
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>GhostLink</title></head>
        <body style="font-family: sans-serif; background: #121212; color: #eee; padding: 50px;">
            <h1>GhostLink API</h1>
            <p>The self-destructing URL shortener is active.</p>
            <ul>
                <li>Use <b>POST /shorten</b> to create links.</li>
                <li>Visit <b>/stats/{code}</b> to check link health.</li>
            </ul>
        </body>
    </html>
    """

@app.post("/shorten")
def shorten_url(payload: LinkCreate):
    print(f"DEBUG: Created ghost link {short_code} for {payload.long_url}")
    with get_db() as conn:
        # Use custom code if provided, otherwise generate one
        short_code = payload.custom_code if payload.custom_code else generate_short_code()
        
        # Check if code already exists
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
def redirect_to_url(short_code: str):
    print(f"DEBUG: Redirecting {short_code} to {link['long_url']}")
    with get_db() as conn:
        link = get_link(conn, short_code)
        
        if not link:
            return HTMLResponse(content=GHOST_PAGE, status_code=404)
        
        # Check Expiration
        # SQLite timestamps are strings; we convert to datetime for comparison
        expires_at = datetime.strptime(link['expires_at'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() > expires_at:
            delete_link(conn, short_code)
            raise HTTPException(status_code=404, detail="Link has vanished.")
        
        # Logic: Increment and check click limit
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