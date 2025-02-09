from fastapi import APIRouter, Depends

from app.db import get_db

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/")
async def generate_bill(purchase_id: str, total_price: float, tax_amount: float, db=Depends(get_db)):
    async with db.acquire() as conn:
        await conn.execute("""
            INSERT INTO billing (purchase_id, total_price, tax_amount,total_amount) 
            VALUES ($1, $2, $3,$4)
        """, purchase_id, total_price, tax_amount)
        return {"message": "Bill generated successfully"}




            