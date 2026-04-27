from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import database as db

class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
        if user_id:
            user = db.get_user(user_id)
            if user and user["is_banned"]:
                if isinstance(event, Message):
                    await event.answer("🚫 <b>Ваш аккаунт заблокирован.</b>", parse_mode="HTML")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Ваш аккаунт заблокирован.", show_alert=True)
                return
        return await handler(event, data)
