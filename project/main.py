from fastapi import FastAPI
from app.routers import products, purchase, billing

app = FastAPI()

app.include_router(products.router)
app.include_router(purchase.router)
app.include_router(billing.router)

@app.get("/")
async def root():
    return {"message": "Billing System API is running!"}













