from fastapi import FastAPI
from app.database import init_db

#initialize db
init_db()

app=FastAPI(title="GhostLink")

@app.get("/")
def health():
    return {"status": "haunting"}
