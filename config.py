import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN","").strip()
ADMIN_IDS={int(x.strip()) for x in os.getenv("ADMIN_IDS","").split(",") if x.strip().isdigit()}
PUBLIC_BASE_URL=os.getenv("PUBLIC_BASE_URL","http://127.0.0.1:8000").rstrip("/")
PORT=int(os.getenv("PORT","8000"))
DATABASE_PATH=os.getenv("DATABASE_PATH","./data/files.db")
ADSTERRA_AD_CODE=os.getenv("ADSTERRA_AD_CODE","")
if not BOT_TOKEN: raise RuntimeError("Set BOT_TOKEN in Koyeb environment variables")
