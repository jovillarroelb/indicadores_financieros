import httpx
from bs4 import BeautifulSoup
import asyncio

async def inspect():
    url = "https://www.sii.cl/valores_y_fechas/dolar/dolar2025.htm"
    print(f"Fetching {url}...")
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        print(f"Status: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        tables = soup.find_all("table")
        print(f"Found {len(tables)} tables.")
        
        for i, t in enumerate(tables):
            print(f"--- Table {i} ---")
            print(f"ID: {t.get('id')}")
            print(f"Classes: {t.get('class')}")
            # Print first few rows text
            rows = t.find_all("tr")
            for j, r in enumerate(rows[:3]):
                print(f"Row {j}: {r.get_text(separator='|', strip=True)}")
            print("\n")

if __name__ == "__main__":
    asyncio.run(inspect())
