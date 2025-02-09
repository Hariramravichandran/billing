import asyncpg


DATABASE_URL = "postgresql://postgres:1527@localhost:5432/billing"

async def create_db_pool():
    return await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

db_pool = None

async def get_db():
    global db_pool
    if db_pool is None:
        db_pool = await create_db_pool()
    return db_pool
