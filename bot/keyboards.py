from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CURRENCIES, LANGUAGES, SUPPORT_USERNAME

def btn(text, cb=None, url=None):
    if url:
        return InlineKeyboardButton(text=text, url=url)
    return InlineKeyboardButton(text=text, callback_data=cb)

def kb(*rows):
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

# ── Переводы кнопок ────────────────────────────────────

BTN_LABELS = {
    "ru": {
        "create_deal":   "📝 Создать сделку",
        "my_deals":      "📋 Мои сделки",
        "verification":  "🔐 Верификация",
        "requisites":    "💳 Реквизиты",
        "language":      "🌐 Язык",
        "referral":      "🔗 Рефералы",
        "about":         "ℹ️ Подробнее",
        "appeals":       "📩 Обращения",
        "support":       "📞 Поддержка",
        "mini_apps":     "📱 Мини-приложения",
        "worker_menu":   "⚙️ Воркер-меню",
        "back_main":     "◀️ Назад в меню",
        "back":          "◀️ Назад",
        "confirm":       "✅ Подтвердить",
        "cancel":        "❌ Отмена",
        "paid":          "✅ Я оплатил",
        "cancel_deal":   "❌ Отменить сделку",
        "cancel_short":  "❌ Отменить",
        "my_deals_btn":  "◀️ Мои сделки",
        "stats":         "📊 Моя статистика",
        "share_ref":     "🔗 Поделиться ссылкой",
        "plat_stats":    "📊 Статистика платформы",
        "suggest":       "💡 Предложить",
        "complaint":     "⚠️ Пожаловаться",
        "apply_verif":   "📤 Подать заявку",
        "deal_link":     "🔗 Ссылка на сделку",
        "complete_deal": "✅ Завершить сделку",
        "set_rating":    "⭐ Установить рейтинг",
        "set_regdate":   "📅 Установить дату регистрации",
        "set_deals":     "📊 Установить кол-во сделок",
    },
    "en": {
        "create_deal":   "📝 Create deal",
        "my_deals":      "📋 My deals",
        "verification":  "🔐 Verification",
        "requisites":    "💳 Requisites",
        "language":      "🌐 Language",
        "referral":      "🔗 Referrals",
        "about":         "ℹ️ About",
        "appeals":       "📩 Appeals",
        "support":       "📞 Support",
        "mini_apps":     "📱 Mini-apps",
        "worker_menu":   "⚙️ Worker menu",
        "back_main":     "◀️ Back to menu",
        "back":          "◀️ Back",
        "confirm":       "✅ Confirm",
        "cancel":        "❌ Cancel",
        "paid":          "✅ I paid",
        "cancel_deal":   "❌ Cancel deal",
        "cancel_short":  "❌ Cancel",
        "my_deals_btn":  "◀️ My deals",
        "stats":         "📊 My statistics",
        "share_ref":     "🔗 Share link",
        "plat_stats":    "📊 Platform statistics",
        "suggest":       "💡 Suggest",
        "complaint":     "⚠️ Complain",
        "apply_verif":   "📤 Apply",
        "deal_link":     "🔗 Deal link",
        "complete_deal": "✅ Complete deal",
        "set_rating":    "⭐ Set rating",
        "set_regdate":   "📅 Set registration date",
        "set_deals":     "📊 Set deals count",
    },
    "uz": {
        "create_deal":   "📝 Bitim yaratish",
        "my_deals":      "📋 Mening bitimlarim",
        "verification":  "🔐 Tasdiqlash",
        "requisites":    "💳 Rekvizitlar",
        "language":      "🌐 Til",
        "referral":      "🔗 Referallar",
        "about":         "ℹ️ Batafsil",
        "appeals":       "📩 Murojaatlar",
        "support":       "📞 Qo'llab-quvvatlash",
        "mini_apps":     "📱 Mini-ilovalar",
        "worker_menu":   "⚙️ Ishchi menyu",
        "back_main":     "◀️ Menyuga qaytish",
        "back":          "◀️ Orqaga",
        "confirm":       "✅ Tasdiqlash",
        "cancel":        "❌ Bekor qilish",
        "paid":          "✅ To'ladim",
        "cancel_deal":   "❌ Bitimni bekor qilish",
        "cancel_short":  "❌ Bekor qilish",
        "my_deals_btn":  "◀️ Mening bitimlarim",
        "stats":         "📊 Mening statistikam",
        "share_ref":     "🔗 Havolani ulashish",
        "plat_stats":    "📊 Platforma statistikasi",
        "suggest":       "💡 Taklif qilish",
        "complaint":     "⚠️ Shikoyat qilish",
        "apply_verif":   "📤 Ariza berish",
        "deal_link":     "🔗 Bitim havolasi",
        "complete_deal": "✅ Bitimni yakunlash",
        "set_rating":    "⭐ Reyting o'rnatish",
        "set_regdate":   "📅 Ro'yxatdan o'tish sanasini o'rnatish",
        "set_deals":     "📊 Bitimlar sonini o'rnatish",
    },
    "tj": {
        "create_deal":   "📝 Эҷоди муомила",
        "my_deals":      "📋 Муомилаҳои ман",
        "verification":  "🔐 Тасдиқ",
        "requisites":    "💳 Реквизитҳо",
        "language":      "🌐 Забон",
        "referral":      "🔗 Рефералҳо",
        "about":         "ℹ️ Муфассал",
        "appeals":       "📩 Муроҷиатҳо",
        "support":       "📞 Дастгирӣ",
        "mini_apps":     "📱 Мини-барномаҳо",
        "worker_menu":   "⚙️ Менюи коргар",
        "back_main":     "◀️ Бозгашт ба меню",
        "back":          "◀️ Бозгашт",
        "confirm":       "✅ Тасдиқ кардан",
        "cancel":        "❌ Бекор кардан",
        "paid":          "✅ Пардохтам",
        "cancel_deal":   "❌ Бекор кардани муомила",
        "cancel_short":  "❌ Бекор кардан",
        "my_deals_btn":  "◀️ Муомилаҳои ман",
        "stats":         "📊 Омори ман",
        "share_ref":     "🔗 Мубодилаи истинод",
        "plat_stats":    "📊 Омори платформа",
        "suggest":       "💡 Пешниҳод кардан",
        "complaint":     "⚠️ Шикоят кардан",
        "apply_verif":   "📤 Ариза додан",
        "deal_link":     "🔗 Истиноди муомила",
        "complete_deal": "✅ Анҷом додани муомила",
        "set_rating":    "⭐ Танзими рейтинг",
        "set_regdate":   "📅 Танзими санаи бақайдгирӣ",
        "set_deals":     "📊 Танзими шумораи муомилаҳо",
    },
    "zh": {
        "create_deal":   "📝 创建交易",
        "my_deals":      "📋 我的交易",
        "verification":  "🔐 验证",
        "requisites":    "💳 收款方式",
        "language":      "🌐 语言",
        "referral":      "🔗 推荐",
        "about":         "ℹ️ 详情",
        "appeals":       "📩 申诉",
        "support":       "📞 支持",
        "mini_apps":     "📱 小程序",
        "worker_menu":   "⚙️ 工作菜单",
        "back_main":     "◀️ 返回菜单",
        "back":          "◀️ 返回",
        "confirm":       "✅ 确认",
        "cancel":        "❌ 取消",
        "paid":          "✅ 我已付款",
        "cancel_deal":   "❌ 取消交易",
        "cancel_short":  "❌ 取消",
        "my_deals_btn":  "◀️ 我的交易",
        "stats":         "📊 我的统计",
        "share_ref":     "🔗 分享链接",
        "plat_stats":    "📊 平台统计",
        "suggest":       "💡 建议",
        "complaint":     "⚠️ 投诉",
        "apply_verif":   "📤 申请",
        "deal_link":     "🔗 交易链接",
        "complete_deal": "✅ 完成交易",
        "set_rating":    "⭐ 设置评分",
        "set_regdate":   "📅 设置注册日期",
        "set_deals":     "📊 设置交易数量",
    },
    "ja": {
        "create_deal":   "📝 取引を作成",
        "my_deals":      "📋 マイ取引",
        "verification":  "🔐 認証",
        "requisites":    "💳 支払い情報",
        "language":      "🌐 言語",
        "referral":      "🔗 紹介",
        "about":         "ℹ️ 詳細",
        "appeals":       "📩 申請",
        "support":       "📞 サポート",
        "mini_apps":     "📱 ミニアプリ",
        "worker_menu":   "⚙️ ワーカーメニュー",
        "back_main":     "◀️ メニューに戻る",
        "back":          "◀️ 戻る",
        "confirm":       "✅ 確認",
        "cancel":        "❌ キャンセル",
        "paid":          "✅ 支払いました",
        "cancel_deal":   "❌ 取引をキャンセル",
        "cancel_short":  "❌ キャンセル",
        "my_deals_btn":  "◀️ マイ取引",
        "stats":         "📊 マイ統計",
        "share_ref":     "🔗 リンクを共有",
        "plat_stats":    "📊 プラットフォーム統計",
        "suggest":       "💡 提案",
        "complaint":     "⚠️ 苦情",
        "apply_verif":   "📤 申請",
        "deal_link":     "🔗 取引リンク",
        "complete_deal": "✅ 取引を完了",
        "set_rating":    "⭐ 評価を設定",
        "set_regdate":   "📅 登録日を設定",
        "set_deals":     "📊 取引数を設定",
    },
    "ar": {
        "create_deal":   "📝 إنشاء صفقة",
        "my_deals":      "📋 صفقاتي",
        "verification":  "🔐 التحقق",
        "requisites":    "💳 بيانات الدفع",
        "language":      "🌐 اللغة",
        "referral":      "🔗 الإحالات",
        "about":         "ℹ️ تفاصيل",
        "appeals":       "📩 الطعون",
        "support":       "📞 الدعم",
        "mini_apps":     "📱 التطبيقات المصغرة",
        "worker_menu":   "⚙️ قائمة العامل",
        "back_main":     "◀️ العودة للقائمة",
        "back":          "◀️ رجوع",
        "confirm":       "✅ تأكيد",
        "cancel":        "❌ إلغاء",
        "paid":          "✅ دفعت",
        "cancel_deal":   "❌ إلغاء الصفقة",
        "cancel_short":  "❌ إلغاء",
        "my_deals_btn":  "◀️ صفقاتي",
        "stats":         "📊 إحصائياتي",
        "share_ref":     "🔗 مشاركة الرابط",
        "plat_stats":    "📊 إحصائيات المنصة",
        "suggest":       "💡 اقتراح",
        "complaint":     "⚠️ شكوى",
        "apply_verif":   "📤 تقديم طلب",
        "deal_link":     "🔗 رابط الصفقة",
        "complete_deal": "✅ إتمام الصفقة",
        "set_rating":    "⭐ تعيين التقييم",
        "set_regdate":   "📅 تعيين تاريخ التسجيل",
        "set_deals":     "📊 تعيين عدد الصفقات",
    },
    "de": {
        "create_deal":   "📝 Deal erstellen",
        "my_deals":      "📋 Meine Deals",
        "verification":  "🔐 Verifizierung",
        "requisites":    "💳 Zahlungsdaten",
        "language":      "🌐 Sprache",
        "referral":      "🔗 Empfehlungen",
        "about":         "ℹ️ Mehr Info",
        "appeals":       "📩 Anfragen",
        "support":       "📞 Support",
        "mini_apps":     "📱 Mini-Apps",
        "worker_menu":   "⚙️ Worker-Menü",
        "back_main":     "◀️ Zurück zum Menü",
        "back":          "◀️ Zurück",
        "confirm":       "✅ Bestätigen",
        "cancel":        "❌ Abbrechen",
        "paid":          "✅ Ich habe bezahlt",
        "cancel_deal":   "❌ Deal abbrechen",
        "cancel_short":  "❌ Abbrechen",
        "my_deals_btn":  "◀️ Meine Deals",
        "stats":         "📊 Meine Statistik",
        "share_ref":     "🔗 Link teilen",
        "plat_stats":    "📊 Plattform-Statistik",
        "suggest":       "💡 Vorschlagen",
        "complaint":     "⚠️ Beschwerde",
        "apply_verif":   "📤 Antrag stellen",
        "deal_link":     "🔗 Deal-Link",
        "complete_deal": "✅ Deal abschließen",
        "set_rating":    "⭐ Bewertung setzen",
        "set_regdate":   "📅 Registrierungsdatum setzen",
        "set_deals":     "📊 Anzahl der Deals setzen",
    },
    "tr": {
        "create_deal":   "📝 Anlaşma oluştur",
        "my_deals":      "📋 Anlaşmalarım",
        "verification":  "🔐 Doğrulama",
        "requisites":    "💳 Ödeme bilgileri",
        "language":      "🌐 Dil",
        "referral":      "🔗 Referanslar",
        "about":         "ℹ️ Hakkında",
        "appeals":       "📩 Başvurular",
        "support":       "📞 Destek",
        "mini_apps":     "📱 Mini uygulamalar",
        "worker_menu":   "⚙️ Çalışan menüsü",
        "back_main":     "◀️ Menüye dön",
        "back":          "◀️ Geri",
        "confirm":       "✅ Onayla",
        "cancel":        "❌ İptal",
        "paid":          "✅ Ödedim",
        "cancel_deal":   "❌ Anlaşmayı iptal et",
        "cancel_short":  "❌ İptal",
        "my_deals_btn":  "◀️ Anlaşmalarım",
        "stats":         "📊 İstatistiklerim",
        "share_ref":     "🔗 Bağlantıyı paylaş",
        "plat_stats":    "📊 Platform istatistikleri",
        "suggest":       "💡 Öneri",
        "complaint":     "⚠️ Şikayet",
        "apply_verif":   "📤 Başvur",
        "deal_link":     "🔗 Anlaşma bağlantısı",
        "complete_deal": "✅ Anlaşmayı tamamla",
        "set_rating":    "⭐ Puan ayarla",
        "set_regdate":   "📅 Kayıt tarihini ayarla",
        "set_deals":     "📊 Anlaşma sayısını ayarla",
    },
}

def L(lang: str, key: str) -> str:
    """Получить перевод кнопки."""
    return BTN_LABELS.get(lang, BTN_LABELS["ru"]).get(key, BTN_LABELS["ru"][key])

def get_lang(user_id: int) -> str:
    """Получить язык пользователя из БД."""
    try:
        import database as db
        u = db.get_user(user_id)
        return u["language"] if u and u["language"] else "ru"
    except Exception:
        return "ru"

# ── Главное меню ───────────────────────────────────────

def main_menu(is_team=False, lang="ru"):
    rows = [
        [btn(L(lang, "create_deal"), "deal_create")],
        [btn(L(lang, "my_deals"), "my_deals"),        btn(L(lang, "verification"), "verification")],
        [btn(L(lang, "requisites"), "requisites"),     btn(L(lang, "language"), "language")],
        [btn(L(lang, "referral"), "referral"),         btn(L(lang, "about"), "about")],
        [btn(L(lang, "appeals"), "appeals")],
        [btn(L(lang, "support"), url=f"https://t.me/{SUPPORT_USERNAME}")],
        [btn(L(lang, "mini_apps"), "mini_apps")],
    ]
    if is_team:
        rows.insert(1, [btn(L(lang, "worker_menu"), "worker_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Выбор типа товара ──────────────────────────────────

def product_type_keyboard(lang="ru"):
    b = btn(L(lang, "back_main"), "back_main")
    return kb(
        [btn("🎴 NFT юзернейм", "ptype_nft_username"), btn("🎁 NFT подарок", "ptype_nft_gift")],
        [btn("📱 Аккаунт", "ptype_tg_account"),        btn("📞 Анонимный номер", "ptype_anon_number")],
        [btn("💬 Чаты/каналы", "ptype_chat_channel"),  btn("💎 Telegram Premium", "ptype_tg_premium")],
        [btn("⭐ Stars", "ptype_tg_stars")],
        [b],
    )

# ── Выбор валюты ───────────────────────────────────────

def currency_keyboard(prefix="cur", lang="ru"):
    icons = {"RUB": "💳", "USD": "💵", "TON": "💎", "STARS": "⭐"}
    rows = []
    for i in range(0, len(CURRENCIES), 2):
        row = [btn(f"{icons[CURRENCIES[i]]} {CURRENCIES[i]}", f"{prefix}_{CURRENCIES[i]}")]
        if i + 1 < len(CURRENCIES):
            row.append(btn(f"{icons[CURRENCIES[i+1]]} {CURRENCIES[i+1]}", f"{prefix}_{CURRENCIES[i+1]}"))
        rows.append(row)
    rows.append([btn(L(lang, "back_main"), "back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Сделка создана ─────────────────────────────────────

def deal_created_kb(deal_id: str, bot_username: str, lang="ru"):
    link = f"https://t.me/{bot_username}?start=deal_{deal_id}"
    return kb(
        [btn(L(lang, "deal_link"), url=link)],
        [btn(L(lang, "my_deals"), "my_deals")],
        [btn(L(lang, "back_main"), "back_main")],
    )

def deal_buyer_kb(deal_id: str, lang="ru"):
    return kb(
        [btn(L(lang, "paid"), f"buyer_paid_{deal_id}")],
        [btn(L(lang, "cancel_deal"), f"deal_cancel_{deal_id}")],
        [btn(L(lang, "back_main"), "back_main")],
    )

def deal_admin_complete_kb(deal_id: str):
    return kb(
        [btn("✅ Завершить сделку", f"admin_complete_{deal_id}")],
        [btn("❌ Отменить сделку", f"admin_cancel_{deal_id}")],
        [btn("◀️ Назад", "admin_disputes")],
    )

def deal_view_kb(deal_id, role, status, lang="ru"):
    rows = []
    if status == "waiting_payment" and role == "buyer":
        rows.append([btn(L(lang, "paid"), f"buyer_paid_{deal_id}")])
    if status in ("pending", "waiting_payment", "checking"):
        rows.append([btn(L(lang, "cancel_short"), f"deal_cancel_{deal_id}")])
    rows.append([btn(L(lang, "my_deals_btn"), "my_deals")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Реквизиты ──────────────────────────────────────────

def requisites_menu(req, lang="ru"):
    def val(v, short=12): return f"{v[:short]}..." if v and len(v) > short else (v or "❌")
    return kb(
        [btn(f"💳 RUB: {val(req['card_rub']) if req else '❌'}", "req_set_card_rub")],
        [btn(f"💵 USD: {val(req['card_usd']) if req else '❌'}", "req_set_card_usd")],
        [btn(f"💎 TON: {val(req['ton_address']) if req else '❌'}", "req_set_ton")],
        [btn(f"🌐 Другое: {val(req['other']) if req else '❌'}", "req_set_other")],
        [btn(L(lang, "back_main"), "back_main")],
    )

# ── Воркер-меню ────────────────────────────────────────

def worker_menu_kb(lang="ru"):
    return kb(
        [btn(L(lang, "set_rating"), "worker_set_rating")],
        [btn(L(lang, "set_regdate"), "worker_set_regdate")],
        [btn(L(lang, "set_deals"), "worker_set_deals")],
        [btn(L(lang, "back_main"), "back_main")],
    )

# ── Язык ───────────────────────────────────────────────

def language_menu(lang="ru"):
    items = list(LANGUAGES.items())
    rows = []
    for i in range(0, len(items), 2):
        row = [btn(items[i][1], f"lang_{items[i][0]}")]
        if i + 1 < len(items):
            row.append(btn(items[i+1][1], f"lang_{items[i+1][0]}"))
        rows.append(row)
    rows.append([btn(L(lang, "back_main"), "back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Рефералы ───────────────────────────────────────────

def referral_menu(bot_username, ref_code, lang="ru"):
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start={ref_code}"
    return kb(
        [btn(L(lang, "stats"), "stats")],
        [btn(L(lang, "share_ref"), url=share_url)],
        [btn(L(lang, "back_main"), "back_main")],
    )

# ── Подробнее ──────────────────────────────────────────

def about_menu(lang="ru"):
    return kb(
        [btn(L(lang, "plat_stats"), "about_stats")],
        [btn(L(lang, "support"), url=f"https://t.me/{SUPPORT_USERNAME}")],
        [btn(L(lang, "back_main"), "back_main")],
    )

# ── Обращения ──────────────────────────────────────────

def appeals_menu(lang="ru"):
    return kb(
        [btn(L(lang, "suggest"), "appeal_suggest")],
        [btn(L(lang, "complaint"), "appeal_complaint")],
        [btn(L(lang, "back_main"), "back_main")],
    )

# ── Верификация ────────────────────────────────────────

def verification_menu(status, lang="ru"):
    rows = []
    if status in ("none", "rejected"):
        rows.append([btn(L(lang, "apply_verif"), "verify_apply")])
    rows.append([btn(L(lang, "back_main"), "back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ── Подтверждение ──────────────────────────────────────

def confirm_kb(action, lang="ru"):
    return kb([btn(L(lang, "confirm"), f"confirm_{action}"), btn(L(lang, "cancel"), "back_main")])

def back_button(target="back_main", lang="ru"):
    label = L(lang, "back_main") if target == "back_main" else L(lang, "back")
    return kb([btn(label, target)])

# ── Админ (всегда RU) ──────────────────────────────────

def admin_panel_kb():
    return kb(
        [btn("📊 Статистика", "admin_stats"),         btn("⚠️ Споры/сделки", "admin_disputes")],
        [btn("🛡 Верификации", "admin_verifications"), btn("🔍 Найти юзера", "admin_find_user")],
        [btn("📩 Обращения", "admin_appeals"),         btn("👥 Воркеры", "admin_workers")],
        [btn("📢 Рассылка", "admin_broadcast")],
        [btn("◀️ Назад в меню", "back_main")],
    )
