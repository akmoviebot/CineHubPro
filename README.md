# FileStream Pro v3 — Universal Multi-Channel

## What changed
- No fixed CHANNEL_ID setting. The same bot can process new media posts in every channel where it is added as an administrator.
- Stores channel title/ID and message ID for each file.
- Automatically adds Stream and Download URL buttons.
- Adsterra HTML/script snippet can be placed in Koyeb environment variable ADSTERRA_AD_CODE and is rendered in two ad slots on the watch page.
- Admin commands: /files, /delete ID, /stats.

## Setup
1. Create bot with @BotFather.
2. Add bot as administrator to each channel. Enable Edit Messages. To publish fallback link notices, enable Post Messages too.
3. Upload this folder to a GitHub repository (do not upload .env).
4. Create a Koyeb Web Service from GitHub.
5. Build command: `pip install -r requirements.txt`
6. Run command: `python main.py`
7. Set Koyeb environment variables: BOT_TOKEN, ADMIN_IDS (your numeric Telegram user ID), PUBLIC_BASE_URL (your Koyeb HTTPS URL), PORT=8000, DATABASE_PATH=./data/files.db.
8. For ads, set ADSTERRA_AD_CODE to the exact ad snippet supplied in your Adsterra publisher dashboard. Keep scripts from trusted Adsterra account only. Check Adsterra rules for allowed placements and user experience.
9. Deploy, then test by posting a video you own or are authorized to distribute in each test channel.

## Important limitations
This is a multi-channel automation starter, not a verified 4 GB production release. Telegram hosted Bot API getFile download links have a 20 MB bot-download limit. 4 GB streaming needs a compatible Local Bot API Server or a suitable authorized storage transport. Koyeb free tier does not guarantee persistent disk, always-on service, unlimited bandwidth or long-running 4 GB transfers. Test before public launch.
SQLite data may reset on redeploy if persistent storage is unavailable. Use a persistent volume or managed database for production. Run only one polling instance. Keep bot token private.
