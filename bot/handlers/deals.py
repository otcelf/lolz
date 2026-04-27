import asyncio
import json
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import texts as t
from config import (PRODUCT_TYPES, PRODUCT_FIELDS, GUARANTEE_FEE,
                    REFERRAL_BONUS, GUARANTOR_PHONE, SUPPORT_USERNAME,
                    SUPPORT_ID, TEAM_CHAT_ID, BOT_USERNAME)
from banner import send_banner

router = Router()

# ── FSM ────────────────────────────────────────────────

class DealFSM(StatesGroup):
    select_type     = State()
    collect_fields  = State()   # сбор полей товара
    select_currency = State()
    enter_amount    = State()
    confirm         = State()

# ── Утилиты ────────────────────────────────────────────

def format_product_info(product_type: str, product_data: dict) -> str:
    lines = []
    labels = {
        "username":     "🎴 Юзернейм",
        "gift_name":    "🎁 Название подарка",
        "account_link": "📱 Аккаунт",
        "account_age":  "📅 Возраст",
        "number":       "📞 Номер",
        "link":         "🔗 Ссылка",
        "subs_count":   "👥 Подписчиков",
        "months":       "💎 Месяцев Premium",
        "target":       "👤 Получатель",
        "amount_stars": "⭐ Количество Stars",
    }
    for k, v in product_data.items():
        label = labels.get(k, k)
        lines.append(f"{label}: <b>{v}</b>")
    return "\n".join(lines) + "\n" if lines else ""

async def is_team_member(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(TEAM_CHAT_ID, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception:
        return False

# ── Старт создания сделки ──────────────────────────────

@router.callback_query(F.data == "deal_create")
async def deal_create(call: CallbackQuery, state: FSMContext):
    if not db.has_any_requisite(call.from_user.id):
        await send_banner(call, t.DEAL_NO_REQUISITES,
            InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Перейти к реквизитам", callback_data="requisites")],
                [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_main")],
            ]))
        return
    await state.set_state(DealFSM.select_type)
    await send_banner(call, t.DEAL_SELECT_TYPE, kb.product_type_keyboard())

# ── Выбор типа товара ──────────────────────────────────

@router.callback_query(F.data.startswith("ptype_"))
async def deal_select_type(call: CallbackQuery, state: FSMContext):
    ptype = call.data.replace("ptype_", "")
    if ptype not in PRODUCT_FIELDS:
        await call.answer("❌ Неизвестный тип", show_alert=True)
        return
    fields = PRODUCT_FIELDS[ptype]
    await state.update_data(product_type=ptype, fields=fields, field_idx=0, product_data={})
    await state.set_state(DealFSM.collect_fields)
    # Показываем красивое меню для первого поля
    await _ask_field(call, fields[0], ptype)

async def _ask_field(target, field_info, ptype):
    field_key, prompt, _ = field_info
    ptype_label = PRODUCT_TYPES.get(ptype, ptype)
    text = (
        f"🔥 <b>Lolz Team Bot</b>\n\n"
        f"📝 <b>Создание сделки — {ptype_label}</b>\n\n"
        f"{prompt}"
    )
    await send_banner(target, text, kb.back_button())

# ── Сбор полей товара ──────────────────────────────────

@router.message(DealFSM.collect_fields)
async def collect_field(message: Message, state: FSMContext):
    data = await state.get_data()
    fields   = data["fields"]
    idx      = data["field_idx"]
    ptype    = data["product_type"]
    prod_data = data["product_data"]

    field_key, _, vtype = fields[idx]
    value = message.text.strip()

    # Валидация
    error = _validate_field(vtype, value)
    if error:
        await send_banner(message, f"🔥 <b>Lolz Team Bot</b>\n\n{error}", kb.back_button(), edit=False)
        return

    prod_data[field_key] = value
    idx += 1

    if idx < len(fields):
        # Следующее поле
        await state.update_data(field_idx=idx, product_data=prod_data)
        await _ask_field(message, fields[idx], ptype)
    else:
        # Все поля собраны — выбор валюты
        await state.update_data(product_data=prod_data)
        await state.set_state(DealFSM.select_currency)
        await send_banner(message, t.DEAL_SELECT_CURRENCY, kb.currency_keyboard("deal_cur"), edit=False)

def _validate_field(vtype: str, value: str) -> str:
    """Возвращает текст ошибки или пустую строку если ок."""
    if vtype == "username":
        v = value.lstrip("@")
        if len(v) < 3 or not v.replace("_", "").isalnum():
            return "❌ <b>Неверный username!</b> <b>Минимум 3 символа, только буквы, цифры и _</b>"
    elif vtype == "phone":
        digits = value.replace("+", "").replace(" ", "")
        if not digits.isdigit() or len(digits) < 10:
            return "❌ <b>Неверный формат номера!</b> <b>Пример: +999XXXXXXX</b>"
    elif vtype == "url":
        if not (value.startswith("http") or value.startswith("t.me") or value.startswith("@")):
            return "❌ <b>Введите корректную ссылку или @username</b>"
    elif vtype == "number":
        if not value.isdigit():
            return "❌ <b>Введите число!</b>"
    elif vtype == "months":
        if value not in ("1", "3", "6", "12"):
            return "❌ <b>Допустимые значения: 1, 3, 6, 12</b>"
    elif vtype == "stars":
        if not value.isdigit() or int(value) < 50:
            return "❌ <b>Минимум 50 Stars!</b>"
    elif vtype == "text":
        if len(value) < 2:
            return "❌ <b>Слишком короткое значение!</b>"
    return ""

# ── Выбор валюты ──────────────────────────────────────

@router.callback_query(F.data.startswith("deal_cur_"))
async def deal_select_currency(call: CallbackQuery, state: FSMContext):
    currency = call.data.replace("deal_cur_", "")
    await state.update_data(currency=currency)
    await state.set_state(DealFSM.enter_amount)
    await send_banner(call, t.DEAL_ENTER_AMOUNT.format(currency=currency), kb.back_button())

# ── Ввод суммы ─────────────────────────────────────────

@router.message(DealFSM.enter_amount)
async def deal_enter_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip().replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n❌ <b>Введите корректную сумму (число больше 0).</b>",
            kb.back_button(), edit=False)
        return

    data = await state.get_data()
    fee   = round(amount * GUARANTEE_FEE / 100, 4)
    total = round(amount + fee, 4)
    await state.update_data(amount=amount, fee=fee, total=total)
    await state.set_state(DealFSM.confirm)

    ptype    = data["product_type"]
    prod_data = data["product_data"]
    currency = data["currency"]
    info_str = format_product_info(ptype, prod_data)

    await send_banner(message,
        t.DEAL_CONFIRM.format(
            product_type=PRODUCT_TYPES.get(ptype, ptype),
            product_info=info_str,
            amount=amount, currency=currency, fee=fee, total=total,
        ),
        kb.confirm_kb("deal"), edit=False)

# ── Подтверждение создания ─────────────────────────────

@router.callback_query(F.data == "confirm_deal", DealFSM.confirm)
async def deal_confirmed(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    ptype     = data["product_type"]
    prod_data = data["product_data"]
    amount    = data["amount"]
    fee       = data["fee"]
    total     = data["total"]
    currency  = data["currency"]

    deal_id = db.create_deal(
        seller_id=call.from_user.id,
        product_type=ptype,
        product_data=json.dumps(prod_data, ensure_ascii=False),
        amount=amount,
        currency=currency,
        fee=fee,
    )

    info_str = format_product_info(ptype, prod_data)
    await send_banner(call,
        t.DEAL_CREATED.format(
            deal_id=deal_id,
            product_type=PRODUCT_TYPES.get(ptype, ptype),
            product_info=info_str,
            amount=amount, currency=currency, fee=fee,
            bot_username=BOT_USERNAME,
        ),
        kb.deal_created_kb(deal_id, BOT_USERNAME))

# ── Покупатель открывает сделку по ссылке ─────────────

async def open_deal_for_buyer(message: Message, deal_id: str, bot: Bot):
    deal = db.get_deal(deal_id)
    if not deal:
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n❌ <b>Сделка не найдена или уже завершена.</b>",
            kb.back_button(), edit=False)
        return
    if deal["status"] not in ("pending",):
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n⚠️ <b>Эта сделка уже недоступна для оплаты.</b>",
            kb.back_button(), edit=False)
        return
    if deal["seller_id"] == message.from_user.id:
        await send_banner(message,
            "🔥 <b>Lolz Team Bot</b>\n\n❌ <b>Вы не можете купить собственный товар.</b>",
            kb.back_button(), edit=False)
        return

    # Привязываем покупателя
    db.update_deal(deal_id, buyer_id=message.from_user.id, status="waiting_payment")

    prod_data = json.loads(deal["product_data"]) if deal["product_data"] else {}
    info_str  = format_product_info(deal["product_type"], prod_data)
    total     = round(deal["amount"] + deal["fee"], 4)

    await send_banner(message,
        t.DEAL_BUYER_VIEW.format(
            deal_id=deal_id,
            product_type=PRODUCT_TYPES.get(deal["product_type"], deal["product_type"]),
            product_info=info_str,
            total=total,
            currency=deal["currency"],
            fee=deal["fee"],
            phone=GUARANTOR_PHONE,
        ),
        kb.deal_buyer_kb(deal_id), edit=False)

# ── Покупатель нажал «Я оплатил» ──────────────────────

@router.callback_query(F.data.startswith("buyer_paid_"))
async def buyer_paid(call: CallbackQuery, bot: Bot):
    deal_id = call.data.replace("buyer_paid_", "")
    deal = db.get_deal(deal_id)

    if not deal or deal["status"] not in ("waiting_payment", "pending"):
        await call.answer("❌ Сделка недоступна", show_alert=True)
        return

    total    = round(deal["amount"] + deal["fee"], 4)
    currency = deal["currency"]
    prod_data = json.loads(deal["product_data"]) if deal["product_data"] else {}
    info_str  = format_product_info(deal["product_type"], prod_data)

    db.update_deal(deal_id, status="checking")

    notify_text = t.DEAL_BUYER_PAID_NOTIFY.format(
        deal_id=deal_id, total=total, currency=currency
    )

    # Уведомляем обоих участников
    await send_banner(call, notify_text, None)
    try:
        await bot.send_message(deal["seller_id"], notify_text, parse_mode="HTML")
    except Exception:
        pass

    # Проверяем — в команде ли покупатель
    buyer_in_team = await is_team_member(bot, call.from_user.id)

    # Ждём 15 секунд
    await asyncio.sleep(15)

    if buyer_in_team:
        # ✅ Оплата подтверждена
        db.update_deal(deal_id, status="paid")
        result_text = t.DEAL_PAYMENT_SUCCESS.format(
            deal_id=deal_id, total=total, currency=currency,
            support=SUPPORT_USERNAME, phone=GUARANTOR_PHONE
        )
        # Уведомляем покупателя
        try:
            await bot.send_message(call.from_user.id, result_text, parse_mode="HTML",
                                   reply_markup=kb.back_button())
        except Exception:
            pass
        # Уведомляем продавца
        try:
            await bot.send_message(deal["seller_id"], result_text, parse_mode="HTML",
                                   reply_markup=kb.back_button())
        except Exception:
            pass
        # Уведомляем гаранта
        seller = db.get_user(deal["seller_id"])
        buyer  = db.get_user(call.from_user.id)
        try:
            await bot.send_message(
                SUPPORT_ID,
                t.GUARANTOR_NOTIFY.format(
                    deal_id=deal_id,
                    product_type=PRODUCT_TYPES.get(deal["product_type"], deal["product_type"]),
                    product_info=info_str,
                    total=total, currency=currency,
                    seller=f"@{seller['username']}" if seller and seller["username"] else str(deal["seller_id"]),
                    buyer=f"@{buyer['username']}" if buyer and buyer["username"] else str(call.from_user.id),
                ),
                parse_mode="HTML",
                reply_markup=kb.deal_admin_complete_kb(deal_id)
            )
        except Exception:
            pass
    else:
        # ❌ Оплата не подтверждена
        db.update_deal(deal_id, status="waiting_payment")
        fail_text = t.DEAL_PAYMENT_FAILED.format(
            deal_id=deal_id, support=SUPPORT_USERNAME
        )
        try:
            await bot.send_message(call.from_user.id, fail_text, parse_mode="HTML",
                                   reply_markup=kb.back_button())
        except Exception:
            pass
        try:
            await bot.send_message(deal["seller_id"], fail_text, parse_mode="HTML",
                                   reply_markup=kb.back_button())
        except Exception:
            pass

# ── Завершение сделки администратором ─────────────────

@router.callback_query(F.data.startswith("admin_complete_"))
async def admin_complete_deal(call: CallbackQuery, bot: Bot):
    from config import ADMIN_IDS
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Нет доступа", show_alert=True)
        return

    deal_id = call.data.replace("admin_complete_", "")
    deal = db.get_deal(deal_id)
    if not deal:
        await call.answer("❌ Сделка не найдена", show_alert=True)
        return

    db.update_deal(deal_id, status="completed")
    db.add_transaction(deal["seller_id"], "deal_income", deal["amount"], deal["currency"],
                       f"Доход по сделке #{deal_id}")

    complete_text = t.DEAL_COMPLETED.format(deal_id=deal_id)

    await send_banner(call, f"✅ <b>Сделка #{deal_id} завершена!</b>", kb.back_button("admin_panel"))

    for uid in filter(None, [deal["seller_id"], deal.get("buyer_id")]):
        try:
            await bot.send_message(uid, complete_text, parse_mode="HTML", reply_markup=kb.back_button())
        except Exception:
            pass

@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel_deal(call: CallbackQuery, bot: Bot):
    from config import ADMIN_IDS
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Нет доступа", show_alert=True)
        return

    deal_id = call.data.replace("admin_cancel_", "")
    db.update_deal(deal_id, status="cancelled")
    cancel_text = t.DEAL_CANCELLED.format(deal_id=deal_id, support=SUPPORT_USERNAME)

    await send_banner(call, f"❌ <b>Сделка #{deal_id} отменена.</b>", kb.back_button("admin_panel"))

    deal = db.get_deal(deal_id)
    if deal:
        for uid in filter(None, [deal["seller_id"], deal.get("buyer_id")]):
            try:
                await bot.send_message(uid, cancel_text, parse_mode="HTML", reply_markup=kb.back_button())
            except Exception:
                pass

# ── Отмена сделки пользователем ────────────────────────

@router.callback_query(F.data.startswith("deal_cancel_"))
async def deal_cancel(call: CallbackQuery, bot: Bot):
    deal_id = call.data.replace("deal_cancel_", "")
    deal = db.get_deal(deal_id)
    if not deal:
        await call.answer("❌ Сделка не найдена", show_alert=True)
        return
    if deal["seller_id"] != call.from_user.id and deal.get("buyer_id") != call.from_user.id:
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    if deal["status"] in ("completed", "cancelled"):
        await call.answer("❌ Сделка уже завершена", show_alert=True)
        return

    db.update_deal(deal_id, status="cancelled")
    cancel_text = t.DEAL_CANCELLED.format(deal_id=deal_id, support=SUPPORT_USERNAME)
    await send_banner(call, cancel_text, kb.back_button())

    other_id = deal["buyer_id"] if deal["seller_id"] == call.from_user.id else deal["seller_id"]
    if other_id:
        try:
            await bot.send_message(other_id, cancel_text, parse_mode="HTML", reply_markup=kb.back_button())
        except Exception:
            pass

# ── Мои сделки ─────────────────────────────────────────

@router.callback_query(F.data == "my_deals")
async def my_deals(call: CallbackQuery):
    deals = db.get_user_deals(call.from_user.id)
    if not deals:
        await send_banner(call, t.MY_DEALS_EMPTY, kb.back_button())
        return

    rows = []
    for d in deals[:10]:
        status = t.DEAL_STATUSES.get(d["status"], d["status"])
        role   = "🛒" if d.get("buyer_id") == call.from_user.id else "💼"
        rows.append([InlineKeyboardButton(
            text=f"{role} #{d['deal_id']} — {d['status'].upper()}",
            callback_data=f"deal_view_{d['deal_id']}"
        )])
    rows.append([InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_main")])

    await send_banner(call, t.MY_DEALS_LIST, InlineKeyboardMarkup(inline_keyboard=rows))

@router.callback_query(F.data.startswith("deal_view_"))
async def deal_view(call: CallbackQuery):
    deal_id = call.data.replace("deal_view_", "")
    deal = db.get_deal(deal_id)
    if not deal:
        await call.answer("❌ Сделка не найдена", show_alert=True)
        return

    role = "🛒 <b>Покупатель</b>" if deal.get("buyer_id") == call.from_user.id else "💼 <b>Продавец</b>"
    prod_data = json.loads(deal["product_data"]) if deal["product_data"] else {}
    info_str  = format_product_info(deal["product_type"], prod_data)
    status_str = t.DEAL_STATUSES.get(deal["status"], deal["status"])
    role_key = "buyer" if deal.get("buyer_id") == call.from_user.id else "seller"

    await send_banner(call,
        t.DEAL_VIEW.format(
            deal_id=deal["deal_id"],
            product_type=PRODUCT_TYPES.get(deal["product_type"], deal["product_type"]),
            product_info=info_str,
            amount=deal["amount"], currency=deal["currency"], fee=deal["fee"],
            status=status_str,
            created_at=deal["created_at"][:10],
            role=role,
        ),
        kb.deal_view_kb(deal_id, role_key, deal["status"])
    )
