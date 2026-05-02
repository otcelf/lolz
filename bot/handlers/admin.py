from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from banner import send_banner
from config import ADMIN_IDS, PRODUCT_TYPES

router = Router()

def is_admin(uid): return uid in ADMIN_IDS

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id): return
    await send_banner(message, "🔥 <b>Lolz Market</b>\n\n⚙️ <b>Панель администратора</b>",
                      kb.admin_panel_kb(), edit=False)

@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Нет доступа", show_alert=True); return
    await send_banner(call, "🔥 <b>Lolz Market</b>\n\n⚙️ <b>Панель администратора</b>", kb.admin_panel_kb())

@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌", show_alert=True); return
    s = db.get_global_stats()
    await send_banner(call,
        f"🔥 <b>Lolz Market</b>\n\n📊 <b>Глобальная статистика</b>\n\n"
        f"👥 <b>Пользователей: {s['users']}</b>\n"
        f"📋 <b>Всего сделок: {s['deals']}</b>\n"
        f"✅ <b>Завершено: {s['completed']}</b>\n"
        f"💰 <b>Оборот (RUB): {round(s['volume_rub'], 2)} ₽</b>",
        kb.back_button("admin_panel"))

@router.callback_query(F.data == "admin_disputes")
async def admin_disputes(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌", show_alert=True); return
    conn = db.get_conn()
    active = conn.execute(
        "SELECT * FROM deals WHERE status IN ('paid','checking','delivering') ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    if not active:
        await send_banner(call,
            "🔥 <b>Lolz Market</b>\n\n⚠️ <b>Активных сделок нет.</b>",
            kb.back_button("admin_panel")); return
    text = f"🔥 <b>Lolz Market</b>\n\n⚠️ <b>Активные сделки ({len(active)})</b>\n\n"
    buttons = []
    for d in active:
        text += f"🆔 <code>{d['deal_id']}</code> <b>— {d['amount']} {d['currency']} [{d['status']}]</b>\n"
        buttons.append([InlineKeyboardButton(
            text=f"#{d['deal_id']} — {d['amount']} {d['currency']}",
            callback_data=f"admin_deal_view_{d['deal_id']}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")])
    await send_banner(call, text, InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("admin_deal_view_"))
async def admin_deal_view(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌", show_alert=True); return
    import json
    deal_id = call.data.replace("admin_deal_view_", "")
    deal = db.get_deal(deal_id)
    if not deal:
        await call.answer("❌ Не найдено", show_alert=True); return
    seller = db.get_user(deal["seller_id"])
    buyer  = db.get_user(deal["buyer_id"]) if deal["buyer_id"] else None
    prod_data = json.loads(deal["product_data"]) if deal["product_data"] else {}
    from handlers.deals import format_product_info
    info_str = format_product_info(deal["product_type"], prod_data)
    await send_banner(call,
        f"🔥 <b>Lolz Market</b>\n\n📋 <b>Сделка #{deal_id}</b>\n\n"
        f"📦 <b>Товар: {PRODUCT_TYPES.get(deal['product_type'], deal['product_type'])}</b>\n"
        f"{info_str}"
        f"💰 <b>Сумма: {deal['amount']} {deal['currency']}</b>\n"
        f"💸 <b>Комиссия: {deal['fee']} {deal['currency']}</b>\n"
        f"📊 <b>Статус: {deal['status']}</b>\n"
        f"👤 <b>Продавец: @{seller['username'] if seller and seller['username'] else deal['seller_id']}</b>\n"
        f"👤 <b>Покупатель: @{buyer['username'] if buyer and buyer['username'] else (deal['buyer_id'] or '—')}</b>",
        kb.deal_admin_complete_kb(deal_id))

@router.callback_query(F.data == "admin_verifications")
async def admin_verifications(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌", show_alert=True); return
    conn = db.get_conn()
    pending = conn.execute("SELECT * FROM verifications WHERE status='pending'").fetchall()
    conn.close()
    if not pending:
        await send_banner(call,
            "🔥 <b>Lolz Market</b>\n\n🛡 <b>Верификации</b>\n\n<b>Заявок нет.</b>",
            kb.back_button("admin_panel")); return
    text = f"🔥 <b>Lolz Market</b>\n\n🛡 <b>Заявки на верификацию ({len(pending)})</b>\n\n"
    buttons = []
    for v in pending:
        u = db.get_user(v["user_id"])
        uname = f"@{u['username']}" if u and u["username"] else str(v["user_id"])
        text += f"👤 <b>{uname} — {v['submitted_at'][:10]}</b>\n"
        buttons.append([
            InlineKeyboardButton(text=f"✅ {uname}", callback_data=f"admin_ver_approve_{v['user_id']}"),
            InlineKeyboardButton(text=f"❌ {uname}", callback_data=f"admin_ver_reject_{v['user_id']}"),
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")])
    await send_banner(call, text, InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("admin_ver_approve_"))
async def admin_ver_approve(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    uid = int(call.data.replace("admin_ver_approve_", ""))
    from datetime import datetime
    conn = db.get_conn()
    conn.execute("UPDATE verifications SET status='approved',reviewed_at=? WHERE user_id=?", (datetime.now().isoformat(), uid))
    conn.execute("UPDATE users SET is_verified=1 WHERE user_id=?", (uid,))
    conn.commit(); conn.close()
    await call.answer("✅ Одобрено", show_alert=True)
    try: await bot.send_message(uid, "🔥 <b>Lolz Market</b>\n\n🎉 <b>Верификация одобрена! Значок ✔️ активирован.</b>", parse_mode="HTML")
    except Exception: pass

@router.callback_query(F.data.startswith("admin_ver_reject_"))
async def admin_ver_reject(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    uid = int(call.data.replace("admin_ver_reject_", ""))
    from datetime import datetime
    conn = db.get_conn()
    conn.execute("UPDATE verifications SET status='rejected',reviewed_at=?,admin_comment='Не соответствует требованиям' WHERE user_id=?", (datetime.now().isoformat(), uid))
    conn.commit(); conn.close()
    await call.answer("❌ Отклонено", show_alert=True)
    try: await bot.send_message(uid, "🔥 <b>Lolz Market</b>\n\n❌ <b>Верификация отклонена.</b>\n\n<b>Причина: Не соответствует требованиям.</b>", parse_mode="HTML")
    except Exception: pass

@router.callback_query(F.data == "admin_appeals")
async def admin_appeals(call: CallbackQuery):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    conn = db.get_conn()
    appeals = conn.execute("SELECT * FROM appeals WHERE status='open' ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    if not appeals:
        await send_banner(call, "🔥 <b>Lolz Market</b>\n\n📩 <b>Обращений нет.</b>", kb.back_button("admin_panel")); return
    text = f"🔥 <b>Lolz Market</b>\n\n📩 <b>Открытые обращения ({len(appeals)})</b>\n\n"
    buttons = []
    for a in appeals:
        icon = "💡" if a["type"] == "suggest" else "⚠️"
        u = db.get_user(a["user_id"])
        uname = f"@{u['username']}" if u and u["username"] else str(a["user_id"])
        text += f"{icon} <code>{a['appeal_id']}</code> <b>— {uname}</b>\n"
        buttons.append([InlineKeyboardButton(text=f"{icon} #{a['appeal_id']}", callback_data=f"admin_appeal_view_{a['appeal_id']}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")])
    await send_banner(call, text, InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("admin_appeal_view_"))
async def admin_appeal_view(call: CallbackQuery):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    appeal_id = call.data.replace("admin_appeal_view_", "")
    conn = db.get_conn()
    a = conn.execute("SELECT * FROM appeals WHERE appeal_id=?", (appeal_id,)).fetchone()
    conn.close()
    if not a: await call.answer("❌", show_alert=True); return
    u = db.get_user(a["user_id"])
    uname = f"@{u['username']}" if u and u["username"] else str(a["user_id"])
    icon = "💡 Предложение" if a["type"] == "suggest" else "⚠️ Жалоба"
    await send_banner(call,
        f"🔥 <b>Lolz Market</b>\n\n📩 <b>Обращение #{appeal_id}</b>\n\n"
        f"📌 <b>Тип: {icon}</b>\n👤 <b>От: {uname}</b>\n📅 <b>{a['created_at'][:16]}</b>\n\n"
        f"<b>{a['text'][:1000]}</b>",
        InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Закрыть", callback_data=f"admin_appeal_close_{appeal_id}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_appeals")],
        ]))

@router.callback_query(F.data.startswith("admin_appeal_close_"))
async def admin_appeal_close(call: CallbackQuery):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    appeal_id = call.data.replace("admin_appeal_close_", "")
    conn = db.get_conn()
    conn.execute("UPDATE appeals SET status='closed' WHERE appeal_id=?", (appeal_id,))
    conn.commit(); conn.close()
    await call.answer("✅ Закрыто", show_alert=True)
    await admin_appeals(call)

@router.callback_query(F.data == "admin_workers")
async def admin_workers(call: CallbackQuery):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    conn = db.get_conn()
    workers = conn.execute("SELECT * FROM users WHERE is_team=1").fetchall()
    conn.close()
    if not workers:
        await send_banner(call, "🔥 <b>Lolz Market</b>\n\n👥 <b>Воркеров нет.</b>", kb.back_button("admin_panel")); return
    text = f"🔥 <b>Lolz Market</b>\n\n👥 <b>Воркеры ({len(workers)})</b>\n\n"
    for w in workers:
        uname = f"@{w['username']}" if w["username"] else str(w["user_id"])
        text += f"👤 <b>{uname}</b> — ⭐ <b>{w['fake_rating'] or '—'}</b> | 📊 <b>{w['fake_deals'] or '—'} сделок</b>\n"
    await send_banner(call, text, kb.back_button("admin_panel"))

# ── Поиск юзера ────────────────────────────────────────

class AdminFindFSM(StatesGroup):
    waiting = State()

@router.callback_query(F.data == "admin_find_user")
async def admin_find_user(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    await state.set_state(AdminFindFSM.waiting)
    await send_banner(call,
        "🔥 <b>Lolz Market</b>\n\n🔍 <b>Введите @username или ID пользователя:</b>",
        kb.back_button("admin_panel"))

@router.message(AdminFindFSM.waiting)
async def admin_find_result(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.clear()
    q = message.text.strip().lstrip("@")
    conn = db.get_conn()
    u = conn.execute("SELECT * FROM users WHERE user_id=?", (int(q),)).fetchone() if q.isdigit() \
        else conn.execute("SELECT * FROM users WHERE username=?", (q,)).fetchone()
    conn.close()
    if not u:
        await send_banner(message, "🔥 <b>Lolz Market</b>\n\n❌ <b>Пользователь не найден.</b>",
                          kb.back_button("admin_panel"), edit=False); return
    deals = db.get_user_deals(u["user_id"])
    completed = sum(1 for d in deals if d["status"] == "completed")
    ban_label = "🔓 Разбанить" if u["is_banned"] else "🚫 Забанить"
    ban_cb    = f"admin_unban_{u['user_id']}" if u["is_banned"] else f"admin_ban_{u['user_id']}"
    await send_banner(message,
        f"🔥 <b>Lolz Market</b>\n\n👤 <b>Пользователь</b>\n\n"
        f"🆔 <b>ID:</b> <code>{u['user_id']}</code>\n"
        f"📛 <b>@{u['username'] or '—'}</b>\n"
        f"📅 <b>Рег: {u['created_at'][:10] if u['created_at'] else '—'}</b>\n"
        f"🛡 <b>Верификация: {'✅' if u['is_verified'] else '❌'}</b>\n"
        f"⚙️ <b>Воркер: {'✅' if u['is_team'] else '❌'}</b>\n"
        f"💳 <b>RUB: {round(u['balance_rub'], 2)} ₽</b>\n"
        f"💎 <b>TON: {round(u['balance_ton'], 4)}</b>\n"
        f"📋 <b>Сделок: {len(deals)} (завершено: {completed})</b>\n"
        f"🚫 <b>Бан: {'Да' if u['is_banned'] else 'Нет'}</b>",
        InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=ban_label, callback_data=ban_cb)],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")],
        ]), edit=False)

@router.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban(call: CallbackQuery):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    uid = int(call.data.replace("admin_ban_", ""))
    conn = db.get_conn(); conn.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (uid,)); conn.commit(); conn.close()
    await call.answer(f"🚫 Забанен", show_alert=True)

@router.callback_query(F.data.startswith("admin_unban_"))
async def admin_unban(call: CallbackQuery):
    if not is_admin(call.from_user.id): await call.answer("❌", show_alert=True); return
    uid = int(call.data.replace("admin_unban_", ""))
    conn = db.get_conn(); conn.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (uid,)); conn.commit(); conn.close()
    await call.answer(f"✅ Разбанен", show_alert=True)

# ── Рассылка ───────────────────────────────────────────

class BroadcastFSM(StatesGroup):
    waiting_message = State()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Нет доступа", show_alert=True); return
    await state.set_state(BroadcastFSM.waiting_message)
    await send_banner(call,
        "🔥 <b>Lolz Market</b>\n\n"
        "📢 <b>Рассылка</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Отправьте сообщение для рассылки.</b>\n\n"
        "<b>Поддерживается:</b>\n"
        "• <b>Текст (с форматированием)</b>\n"
        "• <b>Фото с подписью</b>\n"
        "• <b>Видео с подписью</b>\n\n"
        "⚠️ <b>Сообщение будет отправлено ВСЕМ пользователям!</b>",
        InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_panel")]
        ])
    )

@router.message(BroadcastFSM.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return
    await state.clear()

    # Получаем всех незабаненных пользователей
    conn = db.get_conn()
    users = conn.execute("SELECT user_id FROM users WHERE is_banned=0").fetchall()
    conn.close()

    total   = len(users)
    success = 0
    failed  = 0

    # Уведомляем что рассылка началась
    status_msg = await message.answer(
        f"🔥 <b>Lolz Market</b>\n\n"
        f"📢 <b>Рассылка запущена...</b>\n\n"
        f"👥 <b>Всего пользователей в БД: {total}</b>\n"
        f"⏳ <b>Отправляем...</b>",
        parse_mode="HTML"
    )

    if total == 0:
        await status_msg.edit_text(
            "🔥 <b>Lolz Market</b>\n\n"
            "📢 <b>Рассылка</b>\n\n"
            "⚠️ <b>В базе данных нет пользователей!</b>\n\n"
            "<b>Пользователи появятся после того как они напишут боту /start.</b>",
            parse_mode="HTML",
            reply_markup=kb.admin_panel_kb()
        )
        return

    for user in users:
        try:
            uid = user["user_id"]
            # Копируем сообщение пользователю (поддерживает любой тип)
            await message.copy_to(uid)
            success += 1
        except Exception:
            failed += 1

        # Обновляем статус каждые 50 отправок
        if (success + failed) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"🔥 <b>Lolz Market</b>\n\n"
                    f"📢 <b>Рассылка в процессе...</b>\n\n"
                    f"✅ <b>Отправлено: {success}</b>\n"
                    f"❌ <b>Ошибок: {failed}</b>\n"
                    f"👥 <b>Всего: {total}</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    # Финальный отчёт
    await status_msg.edit_text(
        f"🔥 <b>Lolz Market</b>\n\n"
        f"📢 <b>Рассылка завершена!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Успешно отправлено: {success}</b>\n"
        f"❌ <b>Не доставлено: {failed}</b>\n"
        f"👥 <b>Всего пользователей: {total}</b>\n"
        f"📊 <b>Охват: {round(success/total*100, 1) if total else 0}%</b>",
        parse_mode="HTML",
        reply_markup=kb.admin_panel_kb()
    )
