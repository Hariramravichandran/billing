-- FUNCTION: public.create_purchase(text, jsonb)

-- DROP FUNCTION IF EXISTS public.create_purchase(text, jsonb);

CREATE OR REPLACE FUNCTION public.create_purchase(
	p_customer_email text,
	p_products jsonb)
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    v_purchase_id UUID;
    v_total_amount NUMERIC := 0;
	p_total NUMERIC := 0;
	t_total NUMERIC := 0;
    v_product JSONB;  
    v_product_data RECORD;
    v_total_price NUMERIC;
    v_tax_amount NUMERIC;
BEGIN
    -- Insert purchase record
    INSERT INTO purchases (customer_email) 
    VALUES (p_customer_email) 
    RETURNING id INTO v_purchase_id;
    
    -- Loop through products
    FOR v_product IN SELECT * FROM jsonb_array_elements(p_products) LOOP
        -- Get product details
        SELECT p_name, available_stocks, price, tax_percentage 
        INTO v_product_data
        FROM products 
        WHERE product_id = (v_product->>'product_id')::UUID;
        
        -- Calculate price and tax
        v_total_price := (v_product->>'quantity')::NUMERIC * v_product_data.price;
        v_tax_amount := v_total_price * (v_product_data.tax_percentage / 100);
        
        -- Insert into purchase_items
        INSERT INTO purchase_items (purchase_id, product_id, quantity, price_per_unit, total_price, tax_amount) 
        VALUES (v_purchase_id, (v_product->>'product_id')::UUID, (v_product->>'quantity')::INTEGER, v_product_data.price, v_total_price, v_tax_amount);
        
        -- Accumulate total amount
		p_total :=p_total + v_total_price;
		t_total :=t_total + v_tax_amount;
        v_total_amount := v_total_amount + v_total_price + v_tax_amount;
    END LOOP;
    
    -- Update total amount in purchases table
    UPDATE purchases 
    SET total_amount = v_total_amount
    WHERE id = v_purchase_id;
    
    -- Return the result
    RETURN jsonb_build_object(
        'message', 'Purchase added successfully',
        'purchase_id', v_purchase_id,
		'price',p_total,
		'tax',t_total,
        'total_amount', v_total_amount
    );
END;
$BODY$;

ALTER FUNCTION public.create_purchase(text, jsonb)
    OWNER TO postgres;
