from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok", "msg": "Zero Config + Minimal Deps"}

handler = Mangum(app)
