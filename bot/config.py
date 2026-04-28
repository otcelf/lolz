import os
from dotenv import load_dotenv

# load_dotenv работает локально; на bothost.ru переменные уже в окружении
load_dotenv()

BOT_TOKEN     = os.environ.get("BOT_TOKEN") or os.getenv("BOT_TOKEN", "")
ADMIN_IDS     = list(map(int, os.getenv("ADMIN_IDS", "8659836741").split(",")))
DB_PATH       = os.getenv("DB_PATH", "database.db")

BOT_USERNAME      = "LoIzTeamMarketRobot"
SUPPORT_USERNAME  = "LoIzTeamSupport"
SUPPORT_ID        = 8659836741          # он же админ и гарант
GUARANTOR_PHONE   = "79278171305"       # Сбербанк гаранта
GUARANTOR_TON     = "UQC7I2uPAWAK4pCg1X_UOKARois1aukhczOkTfr8Jy6EeINk"  # TON кошелёк
GUARANTOR_STARS_USERNAME = "LoIzTeamSupport"  # юз для отправки звёзд

# Комиссия Telegram Stars при продаже подарка: получаешь 86% от суммы
# Значит чтобы продавец получил X звёзд, покупатель должен отправить X / 0.86
STARS_COMMISSION = 0.86  # продавец получает 86%
TEAM_CHAT_ID      = -1003887218129      # приватный чат команды

GUARANTEE_FEE  = 3.0
REFERRAL_BONUS = 1.0

MIN_WITHDRAW = {"RUB": 100, "USD": 1, "TON": 0.1, "STARS": 50}
CURRENCIES   = ["RUB", "USD", "TON", "STARS"]

PRODUCT_TYPES = {
    "nft_username": "🎴 NFT юзернейм",
    "nft_gift":     "🎁 NFT подарок",
    "tg_account":   "📱 Аккаунт",
    "anon_number":  "📞 Анонимный номер",
    "chat_channel": "💬 Чаты/каналы",
    "tg_premium":   "💎 Telegram Premium",
    "tg_stars":     "⭐ Stars",
}

# Шаги сбора данных для каждого типа товара
# (field_key, prompt_text, validation_type)
PRODUCT_FIELDS = {
    "nft_username": [
        ("username", "🎴 <b>Введите @юзернейм NFT</b>\n<b>Пример: @cool5</b>", "username"),
    ],
    "nft_gift": [
        ("gift_name", "🎁 <b>Введите точное название NFT подарка:</b>", "text"),
    ],
    "tg_account": [
        ("account_link", "📱 <b>Введите ссылку или @username аккаунта:</b>", "text"),
        ("account_age",  "📅 <b>Укажите возраст аккаунта</b>\n<b>Пример: 3 года</b>", "text"),
    ],
    "anon_number": [
        ("number", "📞 <b>Введите анонимный номер</b>\n<b>Формат: +999XXXXXXX</b>", "phone"),
    ],
    "chat_channel": [
        ("link",       "💬 <b>Введите ссылку на чат/канал:</b>", "url"),
        ("subs_count", "👥 <b>Укажите количество подписчиков:</b>", "number"),
    ],
    "tg_premium": [
        ("months", "💎 <b>На сколько месяцев Premium?</b>\n<b>Варианты: 1 / 3 / 6 / 12</b>", "months"),
        ("target", "👤 <b>Введите @username получателя:</b>", "username"),
    ],
    "tg_stars": [
        ("amount_stars", "⭐ <b>Сколько Stars?</b>\n<b>Минимум: 50</b>", "stars"),
        ("target",       "👤 <b>Введите @username получателя:</b>", "username"),
    ],
}

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇺🇸 English",
    "uz": "🇺🇿 O'zbekcha",
    "tj": "🇹🇯 Тоҷикӣ",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "ar": "🇸🇦 العربية",
    "de": "🇩🇪 Deutsch",
    "tr": "🇹🇷 Türkçe",
}
