from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_dynamic_menu(chat_enabled: bool) -> ReplyKeyboardMarkup:
    button_text = "Выключить чат" if chat_enabled else "Включить чат"
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=button_text)],
            [KeyboardButton(text="Изменить имя"), KeyboardButton(text="Показать опции")]
        ],
        resize_keyboard=True
    )
