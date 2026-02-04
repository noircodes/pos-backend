from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.products import router as products_router
from routers.inventory import router as inventory_router
from routers.orders import router as orders_router

app = FastAPI(title="POS Backend", description="POS APIs")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "ok"}