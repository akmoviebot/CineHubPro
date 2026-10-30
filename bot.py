import logging
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,ContextTypes,filters
from config import BOT_TOKEN,ADMIN_IDS,PUBLIC_BASE_URL
from db import add,recent,disable,stats
logging.basicConfig(level=logging.INFO)
log=logging.getLogger("filestream")
def is_owner(update):
    return bool(update.effective_user and update.effective_user.id in ADMIN_IDS)
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
      "🎬 FileStream Pro — Universal Multi-Channel Bot\n\n"
      "Add me as administrator to any channel where you have permission. "
      "I will detect new video/document/audio posts and attach Stream + Download buttons.\n"
      "/help for commands.")
async def help_cmd(update,context):
    await update.effective_message.reply_text(
      "Owner commands:\n/files — latest files\n/delete ID — disable a link\n/stats — totals and channels\n\n"
      "Setup: add bot as admin to each channel and allow Edit Messages. "
      "It processes new channel posts automatically. Only distribute files you are authorized to share.")
async def on_channel_post(update:Update,context:ContextTypes.DEFAULT_TYPE):
    m=update.channel_post
    if not m:return
    media=m.video or m.document or m.audio
    if not media:return
    title=(getattr(media,"file_name",None) or getattr(media,"title",None) or m.caption or "Untitled file")[:240]
    mime=getattr(media,"mime_type",None)
    size=getattr(media,"file_size",0) or 0
    file_row,token=add(title,media.file_id,getattr(media,"file_unique_id",None),mime,size,
                       m.chat_id,m.chat.title or str(m.chat_id),m.message_id)
    stream=f"{PUBLIC_BASE_URL}/watch/{token}"
    download=f"{PUBLIC_BASE_URL}/download/{token}"
    markup=InlineKeyboardMarkup([[
      InlineKeyboardButton("🖥 Stream",url=stream),
      InlineKeyboardButton("📥 Download",url=download)]])
    try:
        await context.bot.edit_message_reply_markup(chat_id=m.chat_id,message_id=m.message_id,reply_markup=markup)
        log.info("Added links for channel %s post %s",m.chat_id,m.message_id)
    except Exception:
        log.exception("Button edit failed for channel %s",m.chat_id)
        try: await context.bot.send_message(m.chat_id,f"Links for post {m.message_id}:\nStream: {stream}\nDownload: {download}")
        except Exception: log.exception("Could not send fallback links")
async def files_cmd(update,context):
    if not is_owner(update):return
    rows=recent()
    await update.effective_message.reply_text("\n".join(
      f"#{x['id']} | {x['channel_title']} | {x['title']} | {x['file_size']} bytes | {'active' if x['active'] else 'disabled'}"
      for x in rows) or "No files yet.")
async def delete_cmd(update,context):
    if not is_owner(update):return
    if not context.args or not context.args[0].isdigit():
        return await update.effective_message.reply_text("Usage: /delete ID")
    await update.effective_message.reply_text("Link disabled." if disable(int(context.args[0])) else "File not found.")
async def stats_cmd(update,context):
    if not is_owner(update):return
    total,active,channels=stats()
    await update.effective_message.reply_text(f"Total files: {total}\nActive: {active or 0}\nChannels seen: {channels or 0}")
def build():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help_cmd))
    app.add_handler(CommandHandler("files",files_cmd))
    app.add_handler(CommandHandler("delete",delete_cmd))
    app.add_handler(CommandHandler("stats",stats_cmd))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST,on_channel_post))
    return app
