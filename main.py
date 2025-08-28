from fastapi import FastAPI


app = FastAPI(
    title="POS-Backend",
    summary="API related to POS",
)

@app.get("/")
async def read_root():
    return {"message": "Hello World!"}