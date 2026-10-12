
import asyncio
import logging

from core.database import check_database_connection, close_database
from core.logging import logger


async def main() -> None:
    try:
        is_connected = await check_database_connection()

        if is_connected:
            logger.info("Database connection successful.")
        else:
            logger.error("Database health check failed.")

    except Exception:
        logger.exception("Unable to connect to the database.")
        raise

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
