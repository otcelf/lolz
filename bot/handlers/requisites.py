import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import texts as t
from banner import send_banner

router = Router()

class ReqFSM(StatesGroup):
    entering = State()

FIELD_MAP = {
    "req_set_card_rub": "card_rub",
    "req_set_card_usd": "card_usd",
    "req_set_ton":      "ton_address",
    "req_set_other":    "other",
}

def validate(field, value):
    digits = re.sub(r"[\s\-]", "", value)
    if field in ("card_rub", "card_usd"):
        return digits.isdigit() and len(digits) == 16
    if field == "ton_address":
        return len(value) == 48 and (value.startswith("UQ") or value.startswith("EQ"))
    if field == "other":
        return 5 <= len(value.strip()) <= 100
    return False

def _req_text(req):
    return t.REQUISITES.format(
        card_rub=req["card_rub"] if req and req["card_rub"] else "❌ не указана",
        card_usd=req["card_usd"] if req and req["card_usd"] else "❌ не указан",
        ton=req["ton_address"] if req and req["ton_address"] else "❌ не указан",
        other=req["other"] if req and req["other"] else "❌ не указан",
    )

@router.callback_query(F.data == "requisites")
async def requisites_handler(call: CallbackQuery):
    lang = kb.get_lang(call.from_user.id)
    req = db.get_requisites(call.from_user.id)
    await send_banner(call, _req_text(req), kb.requisites_menu(req, lang=lang))

@router.callback_query(F.data.startswith("req_set_"))
async def req_set(call: CallbackQuery, state: FSMContext):
    lang = kb.get_lang(call.from_user.id)
    field = FIELD_MAP.get(call.data)
    if not field:
        return
    await state.update_data(req_field=field)
    await state.set_state(ReqFSM.entering)
    await send_banner(call, t.REQ_ENTER[field], kb.back_button("requisites", lang=lang))

@router.message(ReqFSM.entering)
async def req_enter(message: Message, state: FSMContext):
    lang = kb.get_lang(message.from_user.id)
    data = await state.get_data()
    field = data.get("req_field")
    value = message.text.strip()

    if not validate(field, value):
        await send_banner(message, t.REQ_ERRORS[field], kb.back_button("requisites", lang=lang), edit=False)
        return

    if field in ("card_rub", "card_usd"):
        digits = re.sub(r"[\s\-]", "", value)
        value = " ".join([digits[i:i+4] for i in range(0, 16, 4)])

    db.set_requisite(message.from_user.id, field, value)
    await state.clear()

    req = db.get_requisites(message.from_user.id)
    await send_banner(message,
        "✅ <b>Реквизит сохранён!</b>\n\n" + _req_text(req),
        kb.requisites_menu(req, lang=lang), edit=False)
