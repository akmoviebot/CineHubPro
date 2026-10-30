import os,sqlite3,hashlib,secrets
from datetime import datetime,timedelta,timezone
from config import DATABASE_PATH
def conn():
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".",exist_ok=True)
    c=sqlite3.connect(DATABASE_PATH); c.row_factory=sqlite3.Row; return c
def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY AUTOINCREMENT, token_hash TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL, file_id TEXT NOT NULL, file_unique_id TEXT,
        mime_type TEXT, file_size INTEGER DEFAULT 0, channel_id INTEGER,
        channel_title TEXT, message_id INTEGER, created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL, active INTEGER DEFAULT 1)""")
def add(title,file_id,unique_id,mime,size,channel_id,channel_title,message_id):
    token=secrets.token_urlsafe(32); now=datetime.now(timezone.utc)
    expiry=now+timedelta(days=30)
    with conn() as c:
        cur=c.execute("""INSERT INTO files(token_hash,title,file_id,file_unique_id,mime_type,file_size,
        channel_id,channel_title,message_id,created_at,expires_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (hashlib.sha256(token.encode()).hexdigest(),title,file_id,unique_id,mime,size,
         channel_id,channel_title,message_id,now.isoformat(),expiry.isoformat()))
        return cur.lastrowid,token
def get(token):
    with conn() as c:
        r=c.execute("SELECT * FROM files WHERE token_hash=? AND active=1",
        (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
    if not r:return None
    if datetime.fromisoformat(r["expires_at"])<datetime.now(timezone.utc):return None
    return dict(r)
def recent():
    with conn() as c:return [dict(x) for x in c.execute("SELECT id,title,channel_title,file_size,active FROM files ORDER BY id DESC LIMIT 40")]
def disable(fid):
    with conn() as c:return c.execute("UPDATE files SET active=0 WHERE id=?",(fid,)).rowcount>0
def stats():
    with conn() as c:return c.execute("SELECT COUNT(*),SUM(active),COUNT(DISTINCT channel_id) FROM files").fetchone()
