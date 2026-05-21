from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

kb_builder = InlineKeyboardBuilder()

btn_yes = InlineKeyboardButton(text="Есть", callback_data="yes")
btn_no = InlineKeyboardButton(text="Нет", callback_data='no')
btn_photo = InlineKeyboardButton(text="Есть, с фотографией", callback_data="yes_with_photo")
kb_builder.row(btn_yes,btn_photo,btn_no, width=2)
kb_builder_refresh = InlineKeyboardBuilder()
btn_refresh = InlineKeyboardButton(text="Обновить", callback_data="refresh")
kb_builder_refresh.row(btn_refresh, width=1)