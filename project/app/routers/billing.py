from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.db import get_db
from app.services import generate_bill_pdf, send_email_with_attachment

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/")
async def generate_bill(
    purchase_id: str, 
    total_price: float, 
    tax_amount: float, 
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        # Insert into billing table
        await conn.execute("""
            INSERT INTO billing (purchase_id, total_price, tax_amount, total_amount) 
            VALUES ($1, $2, $3, $4)
        """, purchase_id, total_price, tax_amount, total_price + tax_amount)

        # Mark purchase as billed
        await conn.execute("UPDATE purchases SET bill=True WHERE id=$1", purchase_id)

        # Fetch purchase details
        query = """
        SELECT 
            p.id AS purchase_id,
            p.customer_email,
            p.total_amount,
            COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'product_id', pi.product_id,
                        'quantity', pi.quantity,
                        'price_per_unit', pi.price_per_unit,
                        'total_price', pi.total_price,
                        'tax_amount', pi.tax_amount
                    )
                ) FILTER (WHERE pi.id IS NOT NULL), '[]'::jsonb
            ) AS purchase_items
        FROM purchases p
        LEFT JOIN purchase_items pi ON p.id = pi.purchase_id 
        WHERE p.id=$1
        GROUP BY p.id;
        """
        records = await conn.fetch(query, purchase_id)

        if not records:
            raise HTTPException(status_code=404, detail="No purchases found for the given purchase ID")

        purchase_data = records[0]
    
    # Generate PDF filename
    pdf_filename = f"{purchase_id}_invoice.pdf"
    
    # Generate and send email in background
    background_tasks.add_task(generate_bill_pdf, purchase_data,pdf_filename)
    background_tasks.add_task(send_email_with_attachment, purchase_data["customer_email"], pdf_filename)

    return {"message": "Bill generated and email will be sent shortly!"}





            
