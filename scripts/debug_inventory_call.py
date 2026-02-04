import asyncio
from httpx import AsyncClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import app.main as app_main

async def run():
    from httpx import ASGITransport
    transport = ASGITransport(app=app_main.app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        await client.post('/auth/register', json={"name":"Inv","email":"inv@example.com","username":"inv","password":"secret","role":"admin"})
        r = await client.post('/auth/login', json={"username":"inv","password":"secret"})
        token = r.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        store_id = '000000000000000000000001'
        product_id = '000000000000000000000002'
        r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)
        print('status', r.status_code)
        print('body', r.text)

if __name__ == '__main__':
    asyncio.run(run())
