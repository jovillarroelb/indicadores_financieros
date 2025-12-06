import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime

async def test_sii():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    # Map month number to span ID or text if needed, usually SII uses names
    # But usually the tables are ordered.
    # Actually, inspecting SII UF page: 
    # Tables often have ID 'table_export'. Or inside a div with ID 'mes_diciembre'.
    
    months_es = [
        "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    curr_month_name = months_es[month]

    print(f"Fetching UF for {day}-{curr_month_name}-{year}...")
    
    url = f"https://www.sii.cl/valores_y_fechas/uf/uf{year}.htm"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(f"Status: {r.status_code}")
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Helper to find value in the grid
        # The tables in SII usually are by month.
        # Let's look for a div with ID corresponding to the month, e.g., 'mes_enero'
        # Or look for the table within that div.
        
        # Try to find the specific table for the month
        # Note: SII sometimes changes IDs. Let's try to find the container.
        
        month_div = soup.find("div", id=f"mes_{curr_month_name}")
        if not month_div:
            # Fallback for when "display all" is default or different structure
            print("Month div not found, searching all tables...")
            tables = soup.find_all("table")
            # This is risky without inspecting exact HTML structure.
            # Let's dump a bit of structure if failed.
        else:
            print("Found month div!")
            table = month_div.find("table")
            # Iterate rows looking for the day
            # Table structure is usually: Day | Value | Day | Value ... (multiple columns)
            # Flattening the table is a good strategy.
            
            found_val = None
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                for i, cell in enumerate(cells):
                    txt = cell.get_text(strip=True)
                    if txt == str(day):
                        # The value should be in the next cell? 
                        # Or it's a grid?
                        # Usually SII UF table is:
                        # Day 1 | Day 2 | ...
                        # Val 1 | Val 2 | ...
                        # OR
                        # Day | Val | Day | Val ...
                        
                        # Let's check next sibling in the loop?
                        # Warning: tables can be complex.
                        pass

    # UTM Check
    print(f"\nFetching UTM for {curr_month_name}-{year}...")
    url_utm = f"https://www.sii.cl/valores_y_fechas/utm/utm{year}.htm"
    async with httpx.AsyncClient() as client:
        r = await client.get(url_utm)
        soup = BeautifulSoup(r.text, 'html.parser')
        # UTM table is usually one big table for the year.
        # Rows are months.
        
        # Find row with month name
        # ...

if __name__ == "__main__":
    asyncio.run(test_sii())
