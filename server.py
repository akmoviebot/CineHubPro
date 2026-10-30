import aiohttp
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import HTMLResponse,StreamingResponse,Response,RedirectResponse
from fastapi.templating import Jinja2Templates
from telegram import Bot
from config import BOT_TOKEN,ADSTERRA_AD_CODE
from db import get
app=FastAPI(docs_url=None,redoc_url=None)
templates=Jinja2Templates(directory="templates")
@app.get("/",response_class=HTMLResponse)
async def home():return HTMLResponse("<h2>FileStream Pro is online</h2>")
@app.get("/watch/{token}",response_class=HTMLResponse)
async def watch(request:Request,token:str):
    item=get(token)
    if not item:raise HTTPException(404,"Link invalid, expired or disabled")
    return templates.TemplateResponse("watch.html",{"request":request,"item":item,
      "media_url":f"/stream/{token}","download_url":f"/download/{token}","ad_code":ADSTERRA_AD_CODE})
async def tg_url(item):
    async with Bot(BOT_TOKEN) as bot:
        return (await bot.get_file(item["file_id"])).file_path
@app.api_route("/stream/{token}",methods=["GET","HEAD"])
async def stream(request:Request,token:str):
    item=get(token)
    if not item:raise HTTPException(404,"Link invalid, expired or disabled")
    url=await tg_url(item); headers={}
    if request.headers.get("range"):headers["Range"]=request.headers["range"]
    session=aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None,sock_read=90))
    try:r=await session.get(url,headers=headers)
    except Exception:
        await session.close();raise HTTPException(502,"Telegram upstream unavailable")
    out={k:v for k,v in r.headers.items() if k.lower() in ("content-type","content-length","content-range","accept-ranges")}
    out.setdefault("Accept-Ranges","bytes");out.setdefault("Content-Type",item.get("mime_type") or "application/octet-stream")
    if request.method=="HEAD":
        status=r.status;await r.release();await session.close();return Response(status_code=status,headers=out)
    async def chunks():
        try:
            async for part in r.content.iter_chunked(256*1024):yield part
        finally:r.release();await session.close()
    return StreamingResponse(chunks(),status_code=r.status,headers=out)
@app.get("/download/{token}")
async def download(token:str):
    item=get(token)
    if not item:raise HTTPException(404,"Link invalid, expired or disabled")
    return RedirectResponse(await tg_url(item))
