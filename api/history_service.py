import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

MONTH_MAP = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
}

async def fetch_history_from_sii(indicator: str, year: int) -> List[Dict[str, Any]]:
    ind_lower = indicator.lower()
    
    # Fallback/Alternate for Euro
    if ind_lower == "euro":
         try:
             url = f"https://mindicador.cl/api/euro/{year}"
             def _req_euro():
                 headers = {"User-Agent": "Mozilla/5.0"}
                 return requests.get(url, headers=headers, timeout=3.0, verify=False)
             
             resp = await asyncio.to_thread(_req_euro)
             if resp.status_code == 200:
                 return resp.json().get("serie", [])
             else:
                 logger.warning(f"Mindicador returned {resp.status_code} for Euro")
                 return []
         except Exception as e:
             logger.error(f"Euro fallback failed: {e}")
             return []
    
    base_url = "https://www.sii.cl/valores_y_fechas"
    if ind_lower in ["uf", "uf "]: # handle padding
        url = f"{base_url}/uf/uf{year}.htm"
    elif ind_lower in ["dolar", "usd"]:
        url = f"{base_url}/dolar/dolar{year}.htm"
    elif ind_lower in ["utm"]:
        url = f"{base_url}/utm/utm{year}.htm"
    else:
        logger.warning(f"Unknown indicator for SII: {indicator}")
        return []
        
    results = []
    
    try:
        # logger.info(f"Scraping SII history from {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        def _req_sii():
            return requests.get(url, headers=headers, timeout=4.0, verify=False)

        resp = await asyncio.to_thread(_req_sii)
        if resp.status_code != 200:
            logger.error(f"SII Error {resp.status_code} for {url}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # UTM Format
        if ind_lower == "utm":
            rows = soup.find_all("tr")
            for row in rows:
                cells = row.find_all(["th", "td"])
                if not cells: continue
                
                txt = cells[0].get_text(strip=True).lower()
                
                month_num = 0
                for m_name, m_idx in MONTH_MAP.items():
                    if m_name in txt: 
                        month_num = m_idx
                        break
                
                if month_num > 0:
                    # Value usually in second cell (index 1) or look for digit
                    # cells[0] is month name
                    if len(cells) > 1:
                        val_txt = cells[1].get_text(strip=True)
                        val = parse_sii_value(val_txt)
                        if val:
                            date_str = f"{year}-{month_num:02d}-01T00:00:00.000Z"
                            results.append({"fecha": date_str, "valor": val})
            return results

        # UF / USD Grid Format
        # Locate table. Try multiple IDs.
        table = soup.find("table", id="table_export")
        if not table:
            # Fallback: Look for table with header year
            tables = soup.find_all("table")
            for t in tables:
                if "enero" in t.get_text().lower() or "dia" in t.get_text().lower() or "día" in t.get_text().lower():
                    table = t
                    break
        
        if not table:
            logger.warning("No table found in SII page")
            return []
            
        # Parse Headers
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        
        # If headers are empty (sometimes they use TD for headers), try first TR
        if not headers:
            first_row = table.find("tr")
            if first_row:
                headers = [td.get_text(strip=True).lower() for td in first_row.find_all(["td", "th"])]

        col_map = {}
        for i, h in enumerate(headers):
            for m_name, m_idx in MONTH_MAP.items():
                if m_name in h:
                    col_map[i] = m_idx
                    break
        
        # Rows
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells: continue
            
            # Check for Day in first cell
            day_txt = cells[0].get_text(strip=True)
            if not day_txt.isdigit(): continue
            day = int(day_txt)
            
            # Iterate columns
            for i, cell in enumerate(cells):
                if i == 0: continue # Skip day cell
                
                # Determine month for this column index
                month = col_map.get(i)
                if not month: continue
                
                val_txt = cell.get_text(strip=True)
                val = parse_sii_value(val_txt)
                if val is not None:
                     try:
                         # Check valid date
                         # e.g. Feb 30 will fail
                         datetime(year, month, day)
                         date_str = f"{year}-{month:02d}-{day:02d}T00:00:00.000Z"
                         results.append({"fecha": date_str, "valor": val})
                     except ValueError:
                         pass
        return results

    except Exception as e:
        logger.error(f"Error scraping SII history: {e}")
        return []

def parse_sii_value(text: str) -> Optional[float]:
    if not text: return None
    # Remove dots usually used for thousands in Chile
    # Replace comma with dot for decimals
    clean = text.replace(".", "").replace(",", ".")
    # Check if empty or just whitespace
    if not clean.strip(): return None
    try:
        return float(clean)
    except:
        return None

async def get_history_by_range(indicator: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        start_year = start.year
        end_year = end.year
        
        all_data = []
        
        for y in range(start_year, end_year + 1):
            data = await fetch_history_from_sii(indicator, y)
            all_data.extend(data)
            
        filtered = []
        for item in all_data:
            dt_str = item["fecha"][:10]
            dt = datetime.strptime(dt_str, "%Y-%m-%d")
            if start <= dt <= end:
                filtered.append(item)
                
        filtered.sort(key=lambda x: x["fecha"])
        return filtered
        
    except Exception as e:
        logger.error(f"Error in history range: {e}")
        return []
