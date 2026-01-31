from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статус", callback_data="status")],
        [InlineKeyboardButton(text="🖥 Серверы", callback_data="nodes")],
        [InlineKeyboardButton(text="⚙️ Лимиты", callback_data="limits")]
    ])


def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])
