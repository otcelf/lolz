from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CURRENCIES, LANGUAGES, SUPPORT_USERNAME, PRODUCT_TYPES

def btn(text, cb=None, url=None):
    if url:
        return InlineKeyboardButton(text=text, url=url)
    return InlineKeyboardButton(text=text, callback_data=cb)

def kb(*rows):
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

BACK = btn("◀️ Назад в меню", "back_main")

# ── Главное меню ───────────────────────────────────────

def main_menu(is_team=False):
    rows = [
        [btn("📝 Создать сделку", "deal_create")],
        [btn("📋 Мои сделки", "my_deals"),         btn("🔐 Верификация", "verification")],
        [btn("💳 Реквизиты", "requisites"),         btn("🌐 Язык", "language")],
        [btn("🔗 Рефералы", "referral"),            btn("ℹ️ Подробнее", "about")],
        [btn("📩 Обращения", "appeals")],
        [btn("📞 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [btn("📱 Мини-приложения", "mini_apps")],
    ]
    if is_team:
        rows.insert(1, [btn("⚙️ Воркер-меню", "worker_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Выбор типа товара ──────────────────────────────────

def product_type_keyboard():
    return kb(
        [btn("🎴 NFT юзернейм", "ptype_nft_username"), btn("🎁 NFT подарок", "ptype_nft_gift")],
        [btn("📱 Аккаунт", "ptype_tg_account"),        btn("📞 Анонимный номер", "ptype_anon_number")],
        [btn("💬 Чаты/каналы", "ptype_chat_channel"),  btn("💎 Telegram Premium", "ptype_tg_premium")],
        [btn("⭐ Stars", "ptype_tg_stars")],
        [BACK],
    )

# ── Выбор валюты ───────────────────────────────────────

def currency_keyboard(prefix="cur"):
    icons = {"RUB": "💳", "USD": "💵", "TON": "💎", "STARS": "⭐"}
    rows = []
    for i in range(0, len(CURRENCIES), 2):
        row = [btn(f"{icons[CURRENCIES[i]]} {CURRENCIES[i]}", f"{prefix}_{CURRENCIES[i]}")]
        if i + 1 < len(CURRENCIES):
            row.append(btn(f"{icons[CURRENCIES[i+1]]} {CURRENCIES[i+1]}", f"{prefix}_{CURRENCIES[i+1]}"))
        rows.append(row)
    rows.append([BACK])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Сделка создана — ссылка ────────────────────────────

def deal_created_kb(deal_id: str, bot_username: str):
    link = f"https://t.me/{bot_username}?start=deal_{deal_id}"
    return kb(
        [btn("🔗 Скопировать ссылку на сделку", url=link)],
        [btn("📋 Мои сделки", "my_deals")],
        [BACK],
    )

def deal_buyer_kb(deal_id: str):
    return kb(
        [btn("✅ Я оплатил", f"buyer_paid_{deal_id}")],
        [btn("❌ Отменить сделку", f"deal_cancel_{deal_id}")],
        [BACK],
    )

def deal_admin_complete_kb(deal_id: str):
    return kb(
        [btn("✅ Завершить сделку", f"admin_complete_{deal_id}")],
        [btn("❌ Отменить сделку", f"admin_cancel_{deal_id}")],
        [btn("◀️ Назад", "admin_disputes")],
    )

def my_deals_kb(deals, user_id):
    rows = []
    for d in deals[:10]:
        from texts import DEAL_STATUSES
        status = DEAL_STATUSES.get(d["status"], d["status"])
        rows.append([btn(f"#{d['deal_id']} — {d['status'].upper()}", f"deal_view_{d['deal_id']}")])
    rows.append([BACK])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def deal_view_kb(deal_id, role, status):
    rows = []
    if status == "waiting_payment" and role == "buyer":
        rows.append([btn("✅ Я оплатил", f"buyer_paid_{deal_id}")])
    if status in ("pending", "waiting_payment", "checking"):
        rows.append([btn("❌ Отменить", f"deal_cancel_{deal_id}")])
    rows.append([btn("◀️ Мои сделки", "my_deals")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Реквизиты ──────────────────────────────────────────

def requisites_menu(req):
    def val(v, short=12): return f"{v[:short]}..." if v and len(v) > short else (v or "❌ не указан")
    return kb(
        [btn(f"💳 RUB карта: {val(req['card_rub']) if req else '❌ не указана'}", "req_set_card_rub")],
        [btn(f"💵 USD карта: {val(req['card_usd']) if req else '❌ не указан'}", "req_set_card_usd")],
        [btn(f"💎 TON: {val(req['ton_address']) if req else '❌ не указан'}", "req_set_ton")],
        [btn(f"🌐 Другое: {val(req['other']) if req else '❌ не указан'}", "req_set_other")],
        [BACK],
    )

# ── Воркер-меню ────────────────────────────────────────

def worker_menu_kb():
    return kb(
        [btn("⭐ Установить рейтинг", "worker_set_rating")],
        [btn("📅 Установить дату регистрации", "worker_set_regdate")],
        [btn("📊 Установить кол-во сделок", "worker_set_deals")],
        [BACK],
    )

# ── Язык ───────────────────────────────────────────────

def language_menu():
    items = list(LANGUAGES.items())
    rows = []
    for i in range(0, len(items), 2):
        row = [btn(items[i][1], f"lang_{items[i][0]}")]
        if i + 1 < len(items):
            row.append(btn(items[i+1][1], f"lang_{items[i+1][0]}"))
        rows.append(row)
    rows.append([BACK])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Рефералы ───────────────────────────────────────────

def referral_menu(bot_username, ref_code):
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start={ref_code}"
    return kb(
        [btn("📊 Моя статистика", "stats")],
        [btn("🔗 Поделиться ссылкой", url=share_url)],
        [BACK],
    )

# ── Подробнее ──────────────────────────────────────────

def about_menu():
    return kb(
        [btn("📊 Статистика платформы", "about_stats")],
        [btn("📞 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [BACK],
    )

# ── Обращения ──────────────────────────────────────────

def appeals_menu():
    return kb(
        [btn("💡 Предложить", "appeal_suggest")],
        [btn("⚠️ Пожаловаться", "appeal_complaint")],
        [BACK],
    )

# ── Верификация ────────────────────────────────────────

def verification_menu(status):
    rows = []
    if status in ("none", "rejected"):
        rows.append([btn("📤 Подать заявку", "verify_apply")])
    rows.append([BACK])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Подтверждение ──────────────────────────────────────

def confirm_kb(action):
    return kb([btn("✅ Подтвердить", f"confirm_{action}"), btn("❌ Отмена", "back_main")])

def back_button(target="back_main"):
    label = "◀️ Назад в меню" if target == "back_main" else "◀️ Назад"
    return kb([btn(label, target)])

# ── Админ ──────────────────────────────────────────────

def admin_panel_kb():
    return kb(
        [btn("📊 Статистика", "admin_stats"),        btn("⚠️ Споры/сделки", "admin_disputes")],
        [btn("🛡 Верификации", "admin_verifications"), btn("🔍 Найти юзера", "admin_find_user")],
        [btn("📩 Обращения", "admin_appeals"),        btn("👥 Воркеры", "admin_workers")],
        [BACK],
    )
