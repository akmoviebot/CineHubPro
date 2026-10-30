import asyncio,uvicorn
from config import PORT
from db import init
from bot import build
async def main():
    init();bot=build();await bot.initialize();await bot.start()
    await bot.updater.start_polling(drop_pending_updates=True,allowed_updates=Update.ALL_TYPES)
    try:await uvicorn.Server(uvicorn.Config("server:app",host="0.0.0.0",port=PORT)).serve()
    finally:await bot.updater.stop();await bot.stop();await bot.shutdown()
from telegram import Update
if __name__=="__main__":asyncio.run(main())
