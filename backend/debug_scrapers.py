import asyncio
import httpx
from bs4 import BeautifulSoup

BC_EURO_URL = "https://si3.bcentral.cl/indicadoressiete/secure/Serie.aspx?gcode=PRE_EUR&param=cgBnAE8AOQBlAGcAIwBiAFUALQBsAEcAYgBOAEkASQBCAEcAegBFAFkAeABkADgASAA2AG8AdgB2AFMAUgBYADIAQwBzAEEARQBMAG8ASgBWADQATABrAGQAZAB1ADIAeQBBAFAAZwBhADIAbABWAHcAXwBXAGgATAAkAFIAVAB1AEIAbAB3AFoAdQBRAFgAZwA5AHgAdgAwACQATwBZADcAMwAuAGIARwBFAFIASwAuAHQA"

async def test_bc():
    print("Testing Banco Central Scraper...")
    try:
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.get(BC_EURO_URL, timeout=10.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Content preview:", resp.text[:200])
            else:
                print("Failed BC")
    except Exception as e:
        print(f"Error BC: {e}")

async def test_sii():
    print("Testing SII Scraper...")
    url = "https://www.sii.cl/servicios_online/1047-nomina_inst_financieras-1714.html" # Just an example or typical SII URL
    # Real SII URL used in history_service is likely different.
    # We should import logic from history_service? 
    # But let's just test a basic request to SII to see if it blocks.
    try:
        async with httpx.AsyncClient(verify=False) as client:
             # Basic SII homepage or indicators page
             resp = await client.get("https://www.sii.cl", timeout=10.0)
             print(f"Status SII: {resp.status_code}")
    except Exception as e:
        print(f"Error SII: {e}")

async def main():
    await test_bc()
    await test_sii()

if __name__ == "__main__":
    asyncio.run(main())
