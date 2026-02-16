from fastapi import FastAPI
from app.database import init_db
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
