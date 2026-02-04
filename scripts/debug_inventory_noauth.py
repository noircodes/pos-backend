import asyncio
from httpx import AsyncClient, ASGITransport
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import app.main as app_main

async def run():
    async with AsyncClient(transport=ASGITransport(app=app_main.app), base_url='http://test') as client:
        store_id = '000000000000000000000050'
        product_id = '000000000000000000000051'
        r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "5"})
        print('status', r.status_code)
        try:
            print('json', r.json())
        except Exception:
            print('text', r.text)

if __name__ == '__main__':
    asyncio.run(run())