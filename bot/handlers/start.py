from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import texts as t
from banner import send_banner
from config import TEAM_CHAT_ID

router = Router()

async def check_and_update_team(bot: Bot, user_id: int) -> bool:
    """Проверяет членство в чате команды и обновляет БД."""
    try:
        member = await bot.get_chat_member(TEAM_CHAT_ID, user_id)
        in_team = member.status not in ("left", "kicked", "banned")
    except Exception:
        in_team = False
    db.set_team_status(user_id, 1 if in_team else 0)
    return in_team

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    args = message.text.split()

    if len(args) > 1:
        param = args[1]
        if param.startswith("deal_"):
            deal_id = param.replace("deal_", "")
            from handlers.deals import open_deal_for_buyer
            db.create_user(user.id, user.username or "", user.full_name)
            await check_and_update_team(message.bot, user.id)
            await open_deal_for_buyer(message, deal_id, message.bot)
            return
        conn = db.get_conn()
        ref_user = conn.execute("SELECT user_id FROM users WHERE referral_code=?", (param,)).fetchone()
        conn.close()
        referred_by = ref_user["user_id"] if ref_user and ref_user["user_id"] != user.id else None
        db.create_user(user.id, user.username or "", user.full_name, referred_by)
    else:
        db.create_user(user.id, user.username or "", user.full_name)

    # Проверяем чат команды при каждом /start
    is_team = await check_and_update_team(message.bot, user.id)
    # Участники команды получают верификацию автоматически
    if is_team:
        conn = db.get_conn()
        conn.execute("UPDATE users SET is_verified=1 WHERE user_id=?", (user.id,))
        conn.execute("INSERT OR IGNORE INTO verifications (user_id,status,submitted_at) VALUES(?,?,?)",
                     (user.id, "approved", __import__("datetime").datetime.now().isoformat()))
        conn.execute("UPDATE verifications SET status='approved' WHERE user_id=?", (user.id,))
        conn.commit(); conn.close()
    u = db.get_user(user.id)
    lang = u["language"] if u else "ru"

    await send_banner(
        message,
        t.get_menu_text(user.full_name or user.username or "Пользователь", lang),
        kb.main_menu(is_team=is_team),
        edit=False
    )

@router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    is_team = await check_and_update_team(call.bot, call.from_user.id)
    u = db.get_user(call.from_user.id)
    lang = u["language"] if u else "ru"
    name = call.from_user.full_name or call.from_user.username or "Пользователь"
    await send_banner(call, t.get_menu_text(name, lang), kb.main_menu(is_team=is_team))

@router.callback_query(F.data == "mini_apps")
async def mini_apps(call: CallbackQuery):
    await send_banner(call, t.MINI_APPS, kb.back_button())
