"""
Баннер берётся из файла banner.jpg в корне проекта.
При первой отправке Telegram возвращает file_id — кэшируем его,
чтобы не читать файл каждый раз.
"""
import os
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

# Путь к баннеру — рядом с main.py (т.е. в папке bot/)
_BANNER_PATH = os.path.join(os.path.dirname(__file__), "..", "banner.jpg")
_cached_file_id: str = ""   # кэш file_id после первой отправки


async def send_banner(
    target,
    text: str,
    reply_markup: InlineKeyboardMarkup = None,
    edit: bool = True,
):
    if isinstance(target, CallbackQuery):
        msg = target.message
        if edit:
            await _edit(msg, text, reply_markup)
        else:
            await _send(msg, text, reply_markup)
    else:
        await _send(target, text, reply_markup)


async def _send(msg: Message, text: str, markup):
    global _cached_file_id
    try:
        if _cached_file_id:
            # Используем кэшированный file_id — быстро
            sent = await msg.answer_photo(
                photo=_cached_file_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=markup,
            )
        else:
            # Первый раз — читаем файл с диска
            photo = FSInputFile(_BANNER_PATH)
            sent = await msg.answer_photo(
                photo=photo,
                caption=text,
                parse_mode="HTML",
                reply_markup=markup,
            )
            # Кэшируем file_id для следующих отправок
            if sent.photo:
                _cached_file_id = sent.photo[-1].file_id
    except Exception:
        # Если файл не найден или ошибка — отправляем просто текст
        await msg.answer(text, parse_mode="HTML", reply_markup=markup)


async def _edit(msg: Message, text: str, markup):
    try:
        if msg.photo:
            await msg.edit_caption(caption=text, parse_mode="HTML", reply_markup=markup)
        else:
            await msg.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except TelegramBadRequest:
        await _send(msg, text, markup)
