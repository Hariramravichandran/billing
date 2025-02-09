import json
from fastapi import APIRouter, Depends,Body, HTTPException
from typing import Any, List, Union
from app.db import get_db

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("/")
async def create_purchase(
    customer_email: Union[str, None] = Body(default=None),
    product: Union[List, None] = Body(default=None),
    db=Depends(get_db)
):
    """
    Create a new purchase record in the database.
    
    Returns:
        dict: Confirmation message or error.
    """
    try:
        async with db.acquire() as conn:
            # Convert product list to a JSON string
            product_json = json.dumps(product)
            
            # Pass the JSON string as a JSONB parameter
            query = "SELECT * FROM public.create_purchase($1, $2::jsonb)"
            a = await conn.fetch(query, customer_email, product_json)
            return json.loads(a[0]["create_purchase"])
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the purchase: {str(e)}")


@router.get("/purchase_by_customer")
async def purchase_by_customer(
    customer_email:str,
    db=Depends(get_db)
):
    
    try:
       
        async with db.acquire() as conn:
            
            query = """SELECT 
    p.id AS purchase_id,
    p.customer_email,
    p.total_amount,
    p.paid_amount,
    p.change_amount,
    p.created_at,
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'purchase_item_id', pi.id,
                'product_id', pi.product_id,
                'quantity', pi.quantity,
                'price_per_unit', pi.price_per_unit,
                'total_price', pi.total_price,
                'tax_amount', pi.tax_amount
            )
        ) FILTER (WHERE pi.id IS NOT NULL), '[]'::jsonb
    ) AS purchase_items
FROM purchases p
LEFT JOIN purchase_items pi ON p.id = pi.purchase_id where p.bill=True and p.customer_email=$1
GROUP BY p.id;"""
        records = await conn.fetch(query, customer_email)
        if not records:
            raise HTTPException(status_code=404, detail="No purchases found for the given customer email")
            
        return records
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while getting the purchase details")
