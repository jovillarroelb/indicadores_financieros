import requests
from bs4 import BeautifulSoup
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from models import IndicatorsResponse, Indicator
from history_service import fetch_history_from_sii, get_history_by_range

# Simple Cache
cache = {}
CACHE_TTL = 14400
last_cache_time = None

# URL for Banco Central Euro (from user)
BC_EURO_URL = "https://si3.bcentral.cl/indicadoressiete/secure/Serie.aspx?gcode=PRE_EUR&param=cgBnAE8AOQBlAGcAIwBiAFUALQBsAEcAYgBOAEkASQBCAEcAegBFAFkAeABkADgASAA2AG8AdgB2AFMAUgBYADIAQwBzAEEARQBMAG8ASgBWADQATABrAGQAZAB1ADIAeQBBAFAAZwBhADIAbABWAHcAXwBXAGgATAAkAFIAVAB1AEIAbAB3AFoAdQBRAFgAZwA5AHgAdgAwACQATwBZADcAMwAuAGIARwBFAFIASwAuAHQA"

async def fetch_bc_euro() -> Optional[float]:
    """Scrape Euro from Banco Central."""
    try:
        def _req():
            headers = {"User-Agent": "Mozilla/5.0"}
            return requests.get(BC_EURO_URL, headers=headers, timeout=3.0, verify=False)
        
        resp = await asyncio.to_thread(_req)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Look for table with "Día" in header
        target_table = None
        tables = soup.find_all("table")
        for t in tables:
            if "Día" in t.get_text():
                target_table = t
                break
        
        if not target_table:
            return None
        
        # Find latest value for this month
        # Iterate backwards from today to 1
        now = datetime.now()
        current_day = now.day
        month_idx = now.month
        
        # Map rows by day
        day_values = {}
        rows = target_table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells: continue
            cell0 = cells[0].get_text(strip=True)
            if cell0.isdigit():
                d = int(cell0)
                if month_idx < len(cells):
                    val_txt = cells[month_idx].get_text(strip=True)
                    clean = val_txt.replace(".", "").replace(",", ".")
                    if clean:
                       try:
                           day_values[d] = float(clean)
                       except:
                           pass

        # Find latest
        for d in range(current_day, 0, -1):
            if d in day_values:
                return day_values[d]
                
        return None
    except Exception as e:
        print(f"BC Scraper Error: {e}")
        return None

async def get_past_value(indicator: str, days_ago: int) -> float:
    """Get value from N days ago using history service."""
    target_date = datetime.now() - timedelta(days=days_ago)
    date_str = target_date.strftime("%Y-%m-%d")
    
    # We fetch a range around that date to be safe or just that month/year
    # Efficient: history_service scrapes full year usually.
    # Let's use get_history_by_range logic but optimize?
    # For now, just call get_history_by_range for a small window.
    
    # Actually, we need EXACT date match for variation.
    # If it was a weekend, do we compare to Friday? 
    # Usually variation is vs "Previous Business Day".
    # But user asked for "Daily, Weekly, Monthly".
    # Let's try exact date, if missing (weekend), maybe find nearest previous?
    # Simple logic: exact date first.
    
    try:
        # Fetching strictly for the target date might fail if it's weekend.
        # Let's fetch a 5-day window ending on target_date and take the last available.
        start_window = (target_date - timedelta(days=5)).strftime("%Y-%m-%d")
        data = await get_history_by_range(indicator, start_window, date_str)
        if data:
            return data[-1]["valor"] # Last one is closest to target_date
        return 0.0
    except:
        return 0.0

def calculate_variation(current: float, previous: float) -> float:
    if previous == 0: return 0.0
    return ((current - previous) / previous) * 100

async def fetch_indicators(force_refresh: bool = False) -> IndicatorsResponse:
    if not force_refresh and "indicators" in cache:
        return cache["indicators"]
    
    # 1. Scraping SII for UF, UTM
    # 2. Scraping BC for Euro
    # 3. Mindicador for Dolar (or SII?)
    # User said "Fuente de datos para Euro no es SII". Implies UF/UTM/USD might be okay from SII?
    # Plan says: scraping SII for Real-Time UF/UTM.
    # Let's use SII for USD too if we have the scraper in history?
    # services.py previously used SII for UF, UTM and mindicador for others.
    # Let's keep SII for UF, UTM.
    # Use BC for Euro.
    # Use Mindicador for USD (reliable for observed dollar).
    
    # Parallelize?
    
    indicators = {}
    
    try:
        curr_year = datetime.now().year
        
        # Parallel fetch of full history for the year
        # This reduces sequential waiting time significantly
        # Euro logic separate since it's BC
        
        uf_res, utm_res, usd_res, eur_val = await asyncio.gather(
            fetch_history_from_sii("uf", curr_year),
            fetch_history_from_sii("utm", curr_year),
            fetch_history_from_sii("dolar", curr_year),
            fetch_bc_euro(),
            return_exceptions=True
        )

        # Helper to extract value from history safely
        def extract_vals(hist_list):
            if isinstance(hist_list, list) and hist_list:
                # Sort by date just in case
                hist_list.sort(key=lambda x: x["fecha"])
                curr = hist_list[-1]
                return curr["valor"], curr["fecha"]
            return 0.0, ""

        uf_val, uf_date = extract_vals(uf_res) if isinstance(uf_res, list) else (0, "")
        utm_val, utm_date = extract_vals(utm_res) if isinstance(utm_res, list) else (0, "")
        usd_val, usd_date = extract_vals(usd_res) if isinstance(usd_res, list) else (0, "")
        
        # Euro fallback handling
        if isinstance(eur_val, Exception) or not eur_val:
            eur_val = 0.0
        eur_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        # Build Objects
        ind_uf = Indicator(codigo="uf", nombre="Unidad de Fomento (UF)", unidad_medida="Pesos", valor=uf_val, fecha=uf_date)
        ind_utm = Indicator(codigo="utm", nombre="Unidad Tributaria Mensual (UTM)", unidad_medida="Pesos", valor=utm_val, fecha=utm_date)
        ind_usd = Indicator(codigo="dolar", nombre="Dólar Observado", unidad_medida="Pesos", valor=usd_val, fecha=usd_date)
        ind_eur = Indicator(codigo="euro", nombre="Euro", unidad_medida="Pesos", valor=eur_val, fecha=eur_date)

        # Helper to find past value from IN-MEMORY list
        def find_past(hist_list, days_ago):
            if not isinstance(hist_list, list) or not hist_list: return 0.0
            target_dt = datetime.now() - timedelta(days=days_ago)
            # Find closest date <= target_dt
            # Iterate backwards
            # item["fecha"] is ISO string
            best_val = 0.0
            
            # Simple approach: Search for exact date or nearest previous
            # The list is sorted by date ascending.
            # We want the last item where date <= target_date
            
            for item in reversed(hist_list):
                try:
                    dt = datetime.strptime(item["fecha"][:10], "%Y-%m-%d")
                    if dt.date() <= target_dt.date():
                        return item["valor"]
                except:
                    pass
            return 0.0

        # Calculate Variations using LOCAL data (No more requests!)
        # Euro doesn't have history locally yet (BC scraper is single value).
        # We could implement BC history scraper but for now keep Euro var 0 or fetch separately if critical?
        # Creating a separate 16-call loop just for Euro variation is bad.
        # User accepted 0 previously for Euro variations if no data.
        # Let's keep Euro var as 0 for optimization unless we build BC history scraper.
        
        for (ind, hist) in [(ind_uf, uf_res), (ind_usd, usd_res), (ind_utm, utm_res)]:
            if ind.valor > 0 and isinstance(hist, list):
                prev_1 = find_past(hist, 1)
                prev_7 = find_past(hist, 7)
                prev_30 = find_past(hist, 30)

                ind.valor_ayer = prev_1
                ind.valor_semana = prev_7
                ind.valor_mes = prev_30
                
                ind.variacion_diaria = calculate_variation(ind.valor, prev_1)
                ind.variacion_semanal = calculate_variation(ind.valor, prev_7)
                ind.variacion_mensual = calculate_variation(ind.valor, prev_30)

        result = IndicatorsResponse(
            uf=ind_uf,
            dolar=ind_usd,
            euro=ind_eur,
            utm=ind_utm,
            debug_log="Success"
        )
        
        cache["indicators"] = result
        return result

    except Exception as e:
        import traceback
        err_msg = f"Error: {str(e)} Type: {type(e)} Trace: {traceback.format_exc()}"
        print(f"Error fetching indicators: {err_msg}")
        return IndicatorsResponse(
            uf=Indicator(codigo="uf", nombre="UF", unidad_medida="Pesos", valor=0, fecha=""),
            dolar=Indicator(codigo="dolar", nombre="Dolar", unidad_medida="Pesos", valor=0, fecha=""),
            euro=Indicator(codigo="euro", nombre="Euro", unidad_medida="Pesos", valor=0, fecha=""),
            utm=Indicator(codigo="utm", nombre="UTM", unidad_medida="Pesos", valor=0, fecha=""),
            debug_log=err_msg
        )
