from fastapi import FastAPI
from app.database import init_db
from fastapi import Depends, HTTPException
from app.utils import generate_short_code
from app.crud import create_link,delete_link,increment_clicks,get_link
from app.database import get_db
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from fastapi.responses import RedirectResponse

#initialize db
init_db()

app=FastAPI(title="GhostLink")

class LinkCreate(BaseModel):
    long_url: HttpUrl
    max_clicks: int = 1
    ttl_hours: int = 24

@app.get("/")
def health():
    return {"status": "haunting"}

@app.post("/shorten")
def shorten_url(payload: LinkCreate):
    short_code = generate_short_code()
    
    with get_db() as conn:
        try:
            create_link(
                conn, 
                str(payload.long_url), 
                payload.max_clicks, 
                payload.ttl_hours, 
                short_code
            )
            return {"short_url": f"http://localhost:8000/{short_code}", "short_code": short_code}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Could not create link.")

@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    with get_db() as conn:
        link = get_link(conn, short_code)
        
        if not link:
            raise HTTPException(status_code=404, detail="Link has vanished.")
        
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