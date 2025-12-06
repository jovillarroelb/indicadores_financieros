from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import fetch_indicators
from history_service import get_history_by_range
from models import IndicatorsResponse
from typing import List, Dict, Any

app = FastAPI(
    title="Chilean Economic Indicators API",
    description="API to serve real-time economic indicators (UF, USD, EUR, UTM) and historical data.",
    version="1.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev convenience, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/test")
async def test_endpoint():
    return {"msg": "test ok"}

@app.get("/api/indicators")
async def get_indicators(force: bool = False):
    try:
        data = await fetch_indicators(force_refresh=force)
        return data
    except Exception as e:
        import traceback
        error_info = f"CRITICAL API ERROR: {str(e)} | {traceback.format_exc()}"
        print(error_info)
        return {
            "uf": {"valor": 0, "fecha": "", "codigo": "err", "nombre": "Error", "unidad_medida": ""},
            "dolar": {"valor": 0, "fecha": "", "codigo": "err", "nombre": "Error", "unidad_medida": ""},
            "euro": {"valor": 0, "fecha": "", "codigo": "err", "nombre": "Error", "unidad_medida": ""},
            "utm": {"valor": 0, "fecha": "", "codigo": "err", "nombre": "Error", "unidad_medida": ""},
            "debug_log": error_info
        }

@app.get("/api/history/{indicator}")
async def get_history(indicator: str, start: str, end: str):
    print(f"HIT HISTORY: {indicator} {start} {end}")
    """
    Get historical data for an indicator.
    Params:
      - indicator: UF, USD, EUR, UTM
      - start: YYYY-MM-DD
      - end: YYYY-MM-DD
    """
    data = await get_history_by_range(indicator, start, end)
    if not data and start > end:
         raise HTTPException(status_code=400, detail="Invalid date range")
    return data

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Vercel Handler
from mangum import Mangum
handler = Mangum(app)
