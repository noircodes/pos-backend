import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import app.main as app_main

async def run():
    async with AsyncClient(transport=ASGITransport(app=app_main.app), base_url='http://test') as client:
        uname = 'ord_' + uuid.uuid4().hex[:6]
        await client.post('/auth/register', json={"name":"Ord","email":f"{uname}@example.com","username":uname,"password":"secret","role":"admin"})
        r = await client.post('/auth/login', json={"username": uname,"password":"secret"})
        token = r.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        store_id = '000000000000000000000030'
        product_id = '000000000000000000000031'
        await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "5"}, headers=headers)
        payload = {
            "store_id": store_id,
            "user_id": str('000000000000000000000032'),
            "items": [{"product_id": product_id, "qty": "2", "price": "3.50"}]
        }
        r = await client.post('/orders/', json=payload, headers=headers)
        print('status', r.status_code)
        try:
            print('json', r.json())
        except Exception:
            print('text', r.text)

if __name__ == '__main__':
    asyncio.run(run())
