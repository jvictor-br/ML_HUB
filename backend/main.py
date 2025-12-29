import uvicorn
from fastapi import FastAPI
from database import db

app = FastAPI()

@app.get("/")
async def read_root():
    collections = await db.list_collection_names()
    return {
        "message": "Hello World do Backend (Python)!",
        "status_db": "Conectado",
        "collections": collections
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)