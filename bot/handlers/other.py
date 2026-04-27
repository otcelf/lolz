"""Рефералы, статистика, язык, подробнее, обращения, верификация, мини-приложения."""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import texts as t
from banner import send_banner
from config import ADMIN_IDS, LANGUAGES, SUPPORT_USERNAME, BOT_USERNAME

router = Router()

# ── Рефералы ───────────────────────────────────────────

@router.callback_query(F.data == "referral")
async def referral_handler(call: CallbackQuery, bot: Bot):
    u = db.get_user(call.from_user.id)
    if not u:
        await call.answer("❌ Сначала /start", show_alert=True); return
    bot_info = await bot.get_me()
    referrals = db.get_referrals(call.from_user.id)
    txs = db.get_user_transactions(call.from_user.id, limit=200)
    earned = sum(tx["amount"] for tx in txs if tx["type"] == "referral_bonus")
    await send_banner(call,
        t.REFERRAL.format(
            count=len(referrals), bot_username=bot_info.username,
            ref_code=u["referral_code"], earned=round(earned, 4),
        ),
        kb.referral_menu(bot_info.username, u["referral_code"])
    )

# ── Статистика ─────────────────────────────────────────

@router.callback_query(F.data == "stats")
async def stats_handler(call: CallbackQuery):
    u = db.get_user(call.from_user.id)
    if not u:
        await call.answer("❌ Сначала /start", show_alert=True); return
    deals     = db.get_user_deals(call.from_user.id)
    completed = sum(1 for d in deals if d["status"] == "completed")
    disputed  = sum(1 for d in deals if d["status"] == "disputed")
    volume    = sum(d["amount"] for d in deals if d["status"] == "completed" and d["currency"] == "RUB")
    referrals = db.get_referrals(call.from_user.id)
    txs       = db.get_user_transactions(call.from_user.id, limit=100)
    ref_income = sum(tx["amount"] for tx in txs if tx["type"] == "referral_bonus" and tx["currency"] == "RUB")

    # Используем fake данные если воркер
    total_deals_show = u["fake_deals"] if u["fake_deals"] else len(deals)
    reg_date_show    = u["fake_reg_date"] if u["fake_reg_date"] else (u["created_at"][:10] if u["created_at"] else "—")
    verified = "✅ <b>Верифицирован</b>" if u["is_verified"] else "❌ <b>Не верифицирован</b>"
    username = f"@{u['username']}" if u["username"] else str(u["user_id"])

    await send_banner(call,
        t.STATS.format(
            username=username, verified=verified, reg_date=reg_date_show,
            total_deals=total_deals_show, completed=completed,
            disputed=disputed, volume=round(volume, 2),
            referrals=len(referrals), ref_income=round(ref_income, 2),
        ),
        kb.back_button()
    )

# ── Язык ───────────────────────────────────────────────

@router.callback_query(F.data == "language")
async def language_handler(call: CallbackQuery):
    await send_banner(call, t.LANGUAGE_TEXT, kb.language_menu())

@router.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.replace("lang_", "")
    if lang not in LANGUAGES:
        await call.answer("❌ Неизвестный язык", show_alert=True); return
    db.set_language(call.from_user.id, lang)
    await call.answer(f"✅ Язык изменён на {LANGUAGES[lang]}", show_alert=True)
    u = db.get_user(call.from_user.id)
    await send_banner(call, t.MAIN_MENU, kb.main_menu(is_team=bool(u and u["is_team"])))

# ── Подробнее ──────────────────────────────────────────

@router.callback_query(F.data == "about")
async def about_handler(call: CallbackQuery):
    s = db.get_global_stats()
    await send_banner(call,
        t.ABOUT.format(
            total_deals=s["deals"], completed=s["completed"],
            volume=round(s["volume_rub"], 2), support=SUPPORT_USERNAME,
        ),
        kb.about_menu()
    )

@router.callback_query(F.data == "about_stats")
async def about_stats(call: CallbackQuery):
    s = db.get_global_stats()
    await send_banner(call,
        t.ABOUT.format(
            total_deals=s["deals"], completed=s["completed"],
            volume=round(s["volume_rub"], 2), support=SUPPORT_USERNAME,
        ),
        kb.about_menu()
    )

# ── Обращения ──────────────────────────────────────────

class AppealFSM(StatesGroup):
    entering = State()

@router.callback_query(F.data == "appeals")
async def appeals_handler(call: CallbackQuery):
    await send_banner(call, t.APPEALS, kb.appeals_menu())

@router.callback_query(F.data.startswith("appeal_"))
async def appeal_type(call: CallbackQuery, state: FSMContext):
    atype = call.data.replace("appeal_", "")
    if atype not in ("suggest", "complaint"): return
    await state.update_data(appeal_type=atype)
    await state.set_state(AppealFSM.entering)
    await send_banner(call, t.APPEAL_ENTER[atype], kb.back_button("appeals"))

@router.message(AppealFSM.entering)
async def appeal_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    atype = data.get("appeal_type", "suggest")
    await state.clear()
    appeal_id = db.create_appeal(message.from_user.id, atype, message.text.strip())
    await send_banner(message, t.APPEAL_SENT.format(appeal_id=appeal_id), kb.back_button(), edit=False)
    type_label = "💡 Предложение" if atype == "suggest" else "⚠️ Жалоба"
    for admin_id in ADMIN_IDS:
        try:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await bot.send_message(admin_id,
                f"🔥 <b>Lolz Team Bot</b>\n\n📩 <b>Новое обращение</b>\n\n"
                f"🆔 <code>{appeal_id}</code>\n📌 <b>{type_label}</b>\n"
                f"👤 <b>@{message.from_user.username or message.from_user.id}</b>\n\n"
                f"<b>{message.text[:500]}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="📩 Все обращения", callback_data="admin_appeals")
                ]]))
        except Exception: pass

# ── Верификация ────────────────────────────────────────

class VerifyFSM(StatesGroup):
    waiting_docs = State()

@router.callback_query(F.data == "verification")
async def verification_handler(call: CallbackQuery):
    u = db.get_user(call.from_user.id)
    conn = db.get_conn()
    ver = conn.execute("SELECT * FROM verifications WHERE user_id=?", (call.from_user.id,)).fetchone()
    conn.close()
    if u and u["is_verified"]:
        status_key, extra = "approved", "🎉 <b>Ваш аккаунт верифицирован! Значок ✔️ активен.</b>"
    elif ver:
        status_key = ver["status"]
        extra = {
            "pending":  "⏳ <b>Заявка рассматривается. Ожидайте.</b>",
            "rejected": f"❌ <b>Отклонена.</b>\n💬 <b>Причина: {ver['admin_comment'] or 'не указана'}</b>\n\n<b>Можете подать повторно.</b>",
        }.get(ver["status"], "")
    else:
        status_key, extra = "none", "📝 <b>Нажмите кнопку ниже для подачи заявки.</b>"
    await send_banner(call,
        t.VERIFICATION.format(status=t.VERIFICATION_STATUSES.get(status_key, status_key), extra=extra),
        kb.verification_menu(status_key)
    )

@router.callback_query(F.data == "verify_apply")
async def verify_apply(call: CallbackQuery, state: FSMContext):
    await state.set_state(VerifyFSM.waiting_docs)
    await send_banner(call,
        "🔥 <b>Lolz Team Bot</b>\n\n📤 <b>Подача заявки на верификацию</b>\n\n"
        "<b>Отправьте:</b>\n• <b>Скриншот профиля Telegram</b>\n"
        "• <b>Ссылки на предыдущие сделки (если есть)</b>\n"
        "• <b>Краткое описание деятельности</b>\n\n"
        "<b>Можно несколько сообщений. Напишите /done когда закончите.</b>",
        kb.back_button("verification")
    )

@router.message(VerifyFSM.waiting_docs, F.text == "/done")
async def verify_done(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    from datetime import datetime
    conn = db.get_conn()
    conn.execute("INSERT OR REPLACE INTO verifications (user_id,status,submitted_at) VALUES(?,?,?)",
                 (message.from_user.id, "pending", datetime.now().isoformat()))
    conn.commit(); conn.close()
    await send_banner(message,
        "🔥 <b>Lolz Team Bot</b>\n\n✅ <b>Заявка отправлена!</b>\n\n<b>Рассмотрим в ближайшее время.</b>",
        kb.back_button("verification"), edit=False)
    for admin_id in ADMIN_IDS:
        try:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await bot.send_message(admin_id,
                f"🔥 <b>Lolz Team Bot</b>\n\n🛡 <b>Новая заявка на верификацию</b>\n\n"
                f"👤 <b>@{message.from_user.username or message.from_user.id}</b>\n"
                f"🆔 <code>{message.from_user.id}</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_ver_approve_{message.from_user.id}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_ver_reject_{message.from_user.id}"),
                ]]))
        except Exception: pass

@router.message(VerifyFSM.waiting_docs)
async def verify_collect(message: Message):
    await send_banner(message,
        "🔥 <b>Lolz Team Bot</b>\n\n📎 <b>Получено. Продолжайте или отправьте /done.</b>",
        None, edit=False)
