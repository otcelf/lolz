"""
Воркер-меню — только для участников приватного чата команды.
Позволяет установить рейтинг, дату регистрации, кол-во сделок.
Premium статус выдаётся автоматически.
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import texts as t
from banner import send_banner
from config import TEAM_CHAT_ID

router = Router()

class WorkerFSM(StatesGroup):
    set_rating  = State()
    set_deals   = State()
    set_regdate = State()

async def check_team(bot: Bot, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(TEAM_CHAT_ID, user_id)
        return m.status not in ("left", "kicked", "banned")
    except Exception:
        return False

@router.callback_query(F.data == "worker_menu")
async def worker_menu(call: CallbackQuery, bot: Bot):
    if not await check_team(bot, call.from_user.id):
        await call.answer("❌ Доступ только для участников команды", show_alert=True)
        return
    # Обновляем статус в БД
    db.set_team_status(call.from_user.id, 1)
    u = db.get_user(call.from_user.id)
    await send_banner(call,
        t.WORKER_MENU.format(
            rating=u["fake_rating"] or "не задан",
            deals=u["fake_deals"] or "не задано",
            reg_date=u["fake_reg_date"] or "не задана",
        ),
        kb.worker_menu_kb()
    )

@router.callback_query(F.data == "worker_set_rating")
async def worker_set_rating(call: CallbackQuery, state: FSMContext, bot: Bot):
    if not await check_team(bot, call.from_user.id):
        await call.answer("❌ Нет доступа", show_alert=True); return
    await state.set_state(WorkerFSM.set_rating)
    await send_banner(call, t.WORKER_ENTER_RATING, kb.back_button("worker_menu"))

@router.message(WorkerFSM.set_rating)
async def worker_save_rating(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip().replace(",", "."))
        if not (1.0 <= val <= 5.0):
            raise ValueError
    except ValueError:
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n❌ <b>Введите число от 1.0 до 5.0</b>",
            kb.back_button("worker_menu"), edit=False)
        return
    db.update_worker_profile(message.from_user.id, rating=val)
    await state.clear()
    u = db.get_user(message.from_user.id)
    await send_banner(message,
        t.WORKER_MENU.format(
            rating=u["fake_rating"],
            deals=u["fake_deals"] or "не задано",
            reg_date=u["fake_reg_date"] or "не задана",
        ),
        kb.worker_menu_kb(), edit=False)

@router.callback_query(F.data == "worker_set_deals")
async def worker_set_deals(call: CallbackQuery, state: FSMContext, bot: Bot):
    if not await check_team(bot, call.from_user.id):
        await call.answer("❌ Нет доступа", show_alert=True); return
    await state.set_state(WorkerFSM.set_deals)
    await send_banner(call, t.WORKER_ENTER_DEALS, kb.back_button("worker_menu"))

@router.message(WorkerFSM.set_deals)
async def worker_save_deals(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n❌ <b>Введите целое число!</b>",
            kb.back_button("worker_menu"), edit=False)
        return
    db.update_worker_profile(message.from_user.id, deals=int(message.text.strip()))
    await state.clear()
    u = db.get_user(message.from_user.id)
    await send_banner(message,
        t.WORKER_MENU.format(
            rating=u["fake_rating"] or "не задан",
            deals=u["fake_deals"],
            reg_date=u["fake_reg_date"] or "не задана",
        ),
        kb.worker_menu_kb(), edit=False)

@router.callback_query(F.data == "worker_set_regdate")
async def worker_set_regdate(call: CallbackQuery, state: FSMContext, bot: Bot):
    if not await check_team(bot, call.from_user.id):
        await call.answer("❌ Нет доступа", show_alert=True); return
    await state.set_state(WorkerFSM.set_regdate)
    await send_banner(call, t.WORKER_ENTER_REGDATE, kb.back_button("worker_menu"))

@router.message(WorkerFSM.set_regdate)
async def worker_save_regdate(message: Message, state: FSMContext):
    import re
    val = message.text.strip()
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", val):
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n❌ <b>Неверный формат! Используйте ДД.ММ.ГГГГ</b>",
            kb.back_button("worker_menu"), edit=False)
        return
    db.update_worker_profile(message.from_user.id, reg_date=val)
    await state.clear()
    u = db.get_user(message.from_user.id)
    await send_banner(message,
        t.WORKER_MENU.format(
            rating=u["fake_rating"] or "не задан",
            deals=u["fake_deals"] or "не задано",
            reg_date=u["fake_reg_date"],
        ),
        kb.worker_menu_kb(), edit=False)
