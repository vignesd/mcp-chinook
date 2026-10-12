import asyncio

from core.database import close_database
from tools.album_tools import health_check, get_album


async def main():
    try:
        print((await health_check()).model_dump())
        print((await get_album(1)).model_dump())
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
