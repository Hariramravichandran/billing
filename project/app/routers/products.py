from typing import Union
from fastapi import APIRouter, Body, Depends, HTTPException
from app.db import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/")
async def add_product(
    name: str, available_stocks: int, price: float, tax_percentage: float, db=Depends(get_db)
):
    """
    Add a new product to the database.
    
    Returns:
        dict: Confirmation message with product details.
    """
    try:
        async with db.acquire() as conn:
            result = await conn.fetch(
                """INSERT INTO products (p_name, available_stocks, price, tax_percentage)
                VALUES ($1, $2, $3, $4) RETURNING product_id""", name, available_stocks, price, tax_percentage
            )
            return {"message": "Product added successfully", "id": result[0]["product_id"], "name": name, "stock": available_stocks, "price": price, "tax": tax_percentage}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred while adding the product: {str(error)}")


@router.get("/")
async def list_products(db=Depends(get_db)):
    """
    Retrieve all products from the database.
    
    Returns:
        list: A list of all products.
    """
    try:
        async with db.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM products")
            return rows
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching products: {str(error)}")
    

@router.get("/by_id")
async def products_by_id(id: str, db=Depends(get_db)):
    """
    Retrieve a product by its unique ID.
    
    Returns:
        dict: The product details.
    """
    try:
        async with db.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM products WHERE product_id=$1", id)
            if not rows:
                raise HTTPException(status_code=404, detail="Product not found.")
            return rows[0]
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the product: {str(error)}")
    

@router.put("/update")
async def update_product(
    product_id: str,
    p_name: str = None,
    available_stocks: int = None,
    price: float = None,
    tax_percentage: float = None,
    db=Depends(get_db)
):
    """
    Update product information in the database.
    
    Returns:
        dict: Confirmation message if successful.
    """
    update_data = {"p_name": p_name, "available_stocks": available_stocks, "price": price, "tax_percentage": tax_percentage}
    update_data = {key: value for key, value in update_data.items() if value is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update.")
    
    set_values = ", ".join([f"{col} = ${i + 2}" for i, col in enumerate(update_data.keys())])
    update_query = f"""
        UPDATE products
        SET {set_values}
        WHERE product_id = $1
        RETURNING p_name
    """
    
    try:
        async with db.acquire() as conn:
            result = await conn.fetch(update_query, product_id, *update_data.values())
            if not result:
                raise HTTPException(status_code=404, detail="Product not found.")
            return {"message": f"Product '{result[0]['p_name']}' updated successfully."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the product: {str(error)}")
    
    
@router.delete("/delete")
async def delete_product(id: str, db=Depends(get_db)):
    """
    Delete a product by its unique ID.
    
    Returns:
        dict: Confirmation message.
    """
    try:
        async with db.acquire() as conn:
            result = await conn.execute("DELETE FROM products WHERE product_id=$1", id)
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Product not found.")
            return {"message": "Product deleted successfully."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the product: {str(error)}")


