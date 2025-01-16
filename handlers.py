from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from bot.database import get_user, insert_user, update_user, save_feedback
from bot.keyboard import create_dynamic_menu
from bot.inline_handlers import router as inline_router
from bot.psychologist import get_psychologist_response

class UserState(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State() 

router = Router()
scheduler = AsyncIOScheduler()

async def send_notification(user_id: int, bot: Bot):
    await bot.send_message(user_id, "🥸 Напоминаю, что ты можешь поговорить со мной!")

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user:
        username, chat_enabled = user
        await message.answer(
            f"Добро пожаловать обратно, {username}!",
            reply_markup=create_dynamic_menu(chat_enabled)
        )
    else:
        await insert_user(user_id, {"name": None, "chat_enabled": False})
        await message.answer("🤓 Привет, как мне тебя называть?")
        await state.set_state(UserState.waiting_for_name)

    bot = message.bot
    scheduler.add_job(
        send_notification, 
        trigger=IntervalTrigger(hours=25),
        args=[user_id, bot],
        max_instances=1
    )
    scheduler.start()

@router.message(Command("about"))
async def info_handler(message: Message):
    instruction_text = (
        "📚 *Как этим пользоваться?*\n\n"
        "1️⃣ /start — 🟢 Запуск бота.\n"
        "2️⃣ /about — ℹ️ Инструкции.\n"
        "3️⃣ /feedback — ✍️ Оставить отзыв.\n"
        "4️⃣ 'Включить чат' — 💬 Запуск общения.\n"
        "5️⃣ 'Выключить чат' — 🔕 Прекращение общения.\n"
        "6️⃣ 'Изменить имя' — ✏️ Поменять имя в боте.\n"
        "7️⃣ 'Показать опции' — 🧩 Узнать цитату и совет дня.\n"
    )
    await message.answer(instruction_text, parse_mode="Markdown")

# Обработчик /feedback
@router.message(Command("feedback"))
async def feedback_handler(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_feedback)
    await message.reply("🧐 Пожалуйста, оставьте свой отзыв:")

# Обработчик текста для сохранения отзыва
@router.message(UserState.waiting_for_feedback)
async def save_feedback_handler(message: Message, state: FSMContext):
    feedback_text = message.text
    user_id = message.from_user.id

    # Сохраняем отзыв в базу данных
    await save_feedback(user_id, feedback_text)
    await message.reply("🫶 Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    
    # Сбрасываем состояние
    await state.clear()

@router.message(F.text == "Включить чат")
async def chat_start_handler(message: Message):
    user_id = message.from_user.id
    await update_user(user_id, {"chat_enabled": True})
    await message.answer("✅ Чат включен! Пишите, я вас слышу!", reply_markup=create_dynamic_menu(True))

@router.message(F.text == "Выключить чат")
async def chat_end_handler(message: Message):
    user_id = message.from_user.id
    await update_user(user_id, {"chat_enabled": False})
    await message.answer("❌ Чат выключен! Мы больше не общаемся.", reply_markup=create_dynamic_menu(False))

@router.message(F.text == "Изменить имя")
async def change_username_prompt(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_name)
    await message.reply("🙈 Введите новое имя:")

@router.message(UserState.waiting_for_name)
async def change_username(message: Message, state: FSMContext):
    new_username = message.text
    user_id = message.from_user.id

    await update_user(user_id, {"name": new_username})
    await message.reply(f"👌 Ваше имя изменено на {new_username}!")
    await state.clear()

@router.message(F.text == "Показать опции")
async def show_options_handler(message: Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить совет Дня", callback_data="option_1")],
        [InlineKeyboardButton(text="Получить цитату Дня", callback_data="option_2")]
    ])
    await message.answer("🫡 Выберите опцию ниже:", reply_markup=inline_keyboard)

@router.message()
async def psychologist_conversation_handler(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user and user[1]:  # Проверяем, включен ли чат
        user_message = message.text
        model_response = get_psychologist_response(user_message)
        await message.answer(model_response)
    else:
        await message.answer("❌ Вы не в чате сейчас. Включите чат, чтобы начать разговор.")

router.include_router(inline_router)
