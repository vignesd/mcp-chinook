

# uv run python -c "from core.config import settings; print('App:', settings.app_name); print('Database:', settings.resolved_database_path); print('URL:', settings.database_url)"
# # uv run python -c "import asyncio; from core.database import check_database_connection, close_database; async def_dummy = None"
# uv run python -c "import asyncio; from sqlalchemy import text; from core.database import engine, close_database; exec('async def main():\n async with engine.connect() as c:\n  print((await c.execute(text(\"SELECT COUNT(*) FROM Album\"))).scalar_one())\n await close_database()'); asyncio.run(main())"

# import asyncio;
# from sqlalchemy import text;
# from core.database import engine, close_database;
# exec('async def main():\n async with engine.connect() as c:\n  print((await c.execute(text(\"SELECT COUNT(*) FROM Album\"))).scalar_one())\n await close_database()'); asyncio.run(main())"
# uv run python -c "from tools.album_tools import health_check, server_info, get_album, list_albums, search_albums; print('All five album tools imported successfully')"
