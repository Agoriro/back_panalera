import asyncio

from src.seed_db import seed_database

if __name__ == "__main__":
    asyncio.run(seed_database())
