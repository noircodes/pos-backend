import asyncio
from httpx import AsyncClient, ASGITransport
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import app.main as app_main

async def run():
    async with AsyncClient(transport=ASGITransport(app=app_main.app), base_url='http://test') as client:
        uname = 'inv'
        await client.post('/auth/register', json={"name":"Inv","email":f"{uname}@example.com","username":uname,"password":"secret","role":"admin"})
        r = await client.post('/auth/login', json={"username": uname,"password":"secret"})
        token = r.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        store_id = '000000000000000000000020'
        product_id = '000000000000000000000021'
        r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)
        print('increase status', r.status_code, r.text)
        r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "-3"}, headers=headers)
        print('decrease status', r.status_code, r.text)

if __name__ == '__main__':
    asyncio.run(run())
