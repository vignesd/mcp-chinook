import asyncio

from core.database import close_database
from tools.album_tools import health_check, get_album
from services.customer_services import get_customer_by_email
from tools.customer_tools import get_customer


async def main():
    try:
        # print((await health_check()).model_dump())
        print((await get_album(1)).model_dump())
        print((await get_customer('luisg@embraer.com.br')).model_dump())
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
