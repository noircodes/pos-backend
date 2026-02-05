from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.categories import router as categories_router
from routers.products import router as products_router
from routers.inventory import router as inventory_router
from routers.orders import router as orders_router

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(
    title="POS Backend",
    description="POS APIs",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "ok"}