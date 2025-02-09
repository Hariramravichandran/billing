from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db import get_db

router = APIRouter(prefix="/denomination", tags=["Denomination"])


class Denomination(BaseModel):
    value: int
    count: int
    

@router.get("/")
async def get_available_denominations(db=Depends(get_db)):
    """
    Retrieve all available denominations where count is not zero.
    """
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT value, count FROM denominations_available WHERE count != 0")
        return [Denomination(value=row["value"], count=row["count"]) for row in rows]

@router.post("/", response_model=str)
async def create_denomination(denomination: Denomination, db=Depends(get_db)):
    """
    Create a new denomination with specified value and count.
    """
    async with db.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO public.denominations_available(value, count)
                VALUES($1, $2)""", denomination.value, denomination.count)
            return "Denomination created successfully"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error inserting denomination: {str(e)}")

@router.post("/update", response_model=str)
async def update_denomination(value: int, count: int, db=Depends(get_db)):
    """
    Update the count of an existing denomination.
    """
    async with db.acquire() as conn:
        try:
            result = await conn.execute("""
                UPDATE public.denominations_available
                SET count = $1
                WHERE value = $2""", count, value)
            
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Denomination not found")
            return "Denomination updated successfully"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating denomination: {str(e)}")
