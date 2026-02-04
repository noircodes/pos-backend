import asyncio
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db.mongo import start_session

async def run():
    s = await start_session()
    print('start_session returned:', type(s), s)

asyncio.run(run())
