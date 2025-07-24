
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
import openai
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("🧠 Разобрать идею"), KeyboardButton("📌 Мои задачи"))
main_keyboard.add(KeyboardButton("🌐 Найти инфо"), KeyboardButton("📋 Помощь"))

user_tasks = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.reply("Привет! Я — твой ИИ-ассистент. Чем займемся?", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "🧠 Разобрать идею")
async def analyze_idea(message: Message):
    await message.reply("Опиши идею или гипотезу — я помогу разобрать её по системному мышлению.")

@dp.message_handler(lambda message: message.text == "📌 Мои задачи")
async def show_tasks(message: Message):
    user_id = message.from_user.id
    tasks = user_tasks.get(user_id, [])
    if not tasks:
        await message.reply("У тебя пока нет задач.")
    else:
        task_list = "\n".join(f"— {task}" for task in tasks)
        await message.reply(f"Вот твои задачи:\n{task_list}")

@dp.message_handler(lambda message: message.text == "🌐 Найти инфо")
async def ask_web(message: Message):
    await message.reply("Что ты хочешь найти? Напиши ключевые слова.")

@dp.message_handler(lambda message: message.text == "📋 Помощь")
async def help_menu(message: Message):
    await message.reply("Я могу:\n— Разбирать идеи\n— Искать информацию\n— Вести список задач\nПиши любую гипотезу, и мы разберём её.")

@dp.message_handler()
async def handle_general(message: Message):
    user_id = message.from_user.id
    user_tasks.setdefault(user_id, []).append(message.text)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты аналитик в стиле системного мышления. Помоги разобрать инвестиционную идею."},
            {"role": "user", "content": message.text}
        ]
    )
    await message.reply(response['choices'][0]['message']['content'])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
