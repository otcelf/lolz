from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
import texts as t
from banner import send_banner

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot=None):
    await state.clear()
    user = message.from_user
    args = message.text.split()

    # Обработка реферала или ссылки на сделку
    if len(args) > 1:
        param = args[1]

        # Ссылка на сделку: /start deal_XXXXXXXX
        if param.startswith("deal_"):
            deal_id = param.replace("deal_", "")
            from handlers.deals import open_deal_for_buyer
            db.create_user(user.id, user.username or "", user.full_name)
            await open_deal_for_buyer(message, deal_id, message.bot)
            return

        # Реферальная ссылка
        conn = db.get_conn()
        ref_user = conn.execute("SELECT user_id FROM users WHERE referral_code=?", (param,)).fetchone()
        conn.close()
        referred_by = ref_user["user_id"] if ref_user and ref_user["user_id"] != user.id else None
        db.create_user(user.id, user.username or "", user.full_name, referred_by)
    else:
        db.create_user(user.id, user.username or "", user.full_name)

    # Проверяем — в команде ли
    u = db.get_user(user.id)
    is_team = bool(u and u["is_team"])

    await send_banner(
        message,
        t.WELCOME.format(name=user.full_name or user.username or "Пользователь"),
        kb.main_menu(is_team=is_team),
        edit=False
    )

@router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    u = db.get_user(call.from_user.id)
    is_team = bool(u and u["is_team"])
    await send_banner(call, t.MAIN_MENU, kb.main_menu(is_team=is_team))

@router.callback_query(F.data == "mini_apps")
async def mini_apps(call: CallbackQuery):
    await send_banner(call, t.MINI_APPS, kb.back_button())
