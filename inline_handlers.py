from aiogram import Router, F
from aiogram import types
from aiogram.types import CallbackQuery, Message
from transformers import AutoModelForCausalLM, AutoTokenizer
import random
from datetime import datetime

DAILY_QUOTE_FILE = "daily_quote.txt"
DAILY_ADVICE_FILE = "daily_advice.txt"

router = Router()

def get_daily_advice():
    try:
        with open(DAILY_ADVICE_FILE, "r", encoding="utf-8") as file:
            saved_date, saved_advice = file.readline().split("||")
            if saved_date == datetime.now().strftime("%Y-%m-%d"):
                return saved_advice.strip()
    except FileNotFoundError:
        pass

    with open("advices.txt", "r", encoding="utf-8") as file:
        advice_list = file.readlines()

    new_advice = random.choice(advice_list).strip()
    with open(DAILY_ADVICE_FILE, "w", encoding="utf-8") as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d')}||{new_advice}")

    return new_advice

def get_daily_quote():
    try:
        with open(DAILY_QUOTE_FILE, "r", encoding="utf-8") as file:
            saved_date, saved_quote = file.readline().split("||")
            if saved_date == datetime.now().strftime("%Y-%m-%d"):
                return saved_quote.strip()
    except FileNotFoundError:
        pass

    with open("quotes.txt", "r", encoding="utf-8") as file:
        quotes_list = file.readlines()

    new_quote = random.choice(quotes_list).strip()
    with open(DAILY_QUOTE_FILE, "w", encoding="utf-8") as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d')}||{new_quote}")

    return new_quote

@router.callback_query(F.data == "option_1")
async def option_1_handler(callback_query: CallbackQuery):
    advice = get_daily_advice()
    await callback_query.answer()
    await callback_query.message.answer(f"🙇 Совет дня: {advice}")

@router.callback_query(F.data == "option_2")
async def option_2_handler(callback_query: CallbackQuery):
    quote = get_daily_quote()
    await callback_query.answer()
    await callback_query.message.answer(f"🤔 Цитата дня: {quote}")
