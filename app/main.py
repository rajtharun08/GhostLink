from fastapi import FastAPI
from app.database import init_db
from fastapi import Depends, HTTPException
from app.utils import generate_short_code
from app.crud import create_link
from app.database import get_db
from pydantic import BaseModel, HttpUrl

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
