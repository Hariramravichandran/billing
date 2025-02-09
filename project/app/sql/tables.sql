CREATE TABLE IF NOT EXISTS public.products
(
    product_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    p_name text COLLATE pg_catalog."default" NOT NULL,
    available_stocks integer DEFAULT 0,
    price double precision NOT NULL,
    tax_percentage double precision NOT NULL,
    CONSTRAINT products_pkey PRIMARY KEY (product_id)
)


CREATE TABLE IF NOT EXISTS public.purchases
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    customer_email text COLLATE pg_catalog."default" NOT NULL,
    total_amount double precision,
    paid_amount double precision,
    change_amount double precision,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    bill boolean DEFAULT false,
    CONSTRAINT purchases_pkey PRIMARY KEY (id)
)


CREATE TABLE IF NOT EXISTS public.purchase_items
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    purchase_id uuid NOT NULL,
    product_id uuid NOT NULL,
    quantity integer NOT NULL,
    price_per_unit double precision NOT NULL,
    total_price double precision NOT NULL,
    tax_amount double precision NOT NULL,
    CONSTRAINT purchase_items_pkey PRIMARY KEY (id),
    CONSTRAINT purchase_items_product_id_fkey FOREIGN KEY (product_id)
        REFERENCES public.products (product_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT purchase_items_purchase_id_fkey FOREIGN KEY (purchase_id)
        REFERENCES public.purchases (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)


CREATE TABLE IF NOT EXISTS public.invoices
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    purchase_id uuid NOT NULL,
    invoice_pdf bytea,
    sent_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT invoices_pkey PRIMARY KEY (id),
    CONSTRAINT invoices_purchase_id_key UNIQUE (purchase_id),
    CONSTRAINT invoices_purchase_id_fkey FOREIGN KEY (purchase_id)
        REFERENCES public.purchases (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)


CREATE TABLE IF NOT EXISTS public.billing
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    purchase_id uuid NOT NULL,
    total_price double precision NOT NULL,
    tax_amount double precision NOT NULL,
    total_amount double precision,
    CONSTRAINT billing_pkey PRIMARY KEY (id),
    CONSTRAINT billing_purchase_id_fkey FOREIGN KEY (purchase_id)
        REFERENCES public.purchases (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS public.denominations_available
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    value integer NOT NULL,
    count integer DEFAULT 0,
    CONSTRAINT denominations_available_pkey PRIMARY KEY (id),
    CONSTRAINT denominations_available_value_key UNIQUE (value)
)

CREATE TABLE IF NOT EXISTS public.change_given
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    purchase_id uuid NOT NULL,
    denomination_value integer NOT NULL,
    count integer NOT NULL,
    CONSTRAINT change_given_pkey PRIMARY KEY (id),
    CONSTRAINT change_given_purchase_id_fkey FOREIGN KEY (purchase_id)
        REFERENCES public.purchases (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)