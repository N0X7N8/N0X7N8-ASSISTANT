import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ==========================================
# НАСТРОЙКИ (ВСТАВЬ ТОЛЬКО ТОКЕН)
# ==========================================
BOT_TOKEN = "9229688867:AAFRK93k-Ulh-T-SjGsvik8Gd3ROhMZS83U"
ADMIN_ID = 7969586047  # Твой ID уже вписан

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# СОСТОЯНИЯ (FSM)
# ==========================================
class OrderForm(StatesGroup):
    choosing_service = State()
    entering_name = State()
    entering_description = State()
    entering_references = State()
    entering_deadline = State()

# ==========================================
# КЛАВИАТУРЫ
# ==========================================
def get_services_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🌐 Сайт")
    builder.button(text="🤖 Бот")
    builder.button(text="🎮 Скрипт")
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# ХЕНДЛЕРЫ
# ==========================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я бот-помощник NOX7N8. Здесь вы можете заказать разработку.\n"
        "Выберите, что вас интересует:",
        reply_markup=get_services_kb()
    )
    await state.set_state(OrderForm.choosing_service)

@dp.message(OrderForm.choosing_service)
async def process_service(message: types.Message, state: FSMContext):
    if message.text not in ["🌐 Сайт", "🤖 Бот", "🎮 Скрипт"]:
        await message.answer("Пожалуйста, выберите услугу из кнопок ниже 👇")
        return

    await state.update_data(service=message.text)
    await message.answer(
        f"Отлично! Вы хотите заказать: {message.text}.\n"
        "Как я могу к вам обращаться? (Напишите ваше имя или ник)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(OrderForm.entering_name)

@dp.message(OrderForm.entering_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"Приятно познакомиться, {message.text}!\n"
        "Опишите, что именно вам нужно сделать (ваши пожелания, функции, стиль)."
    )
    await state.set_state(OrderForm.entering_description)

@dp.message(OrderForm.entering_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "Есть ли у вас примеры или референсы (ссылки на сайты, которые нравятся)?\n"
        "Если нет — напишите 'Нет'."
    )
    await state.set_state(OrderForm.entering_references)

@dp.message(OrderForm.entering_references)
async def process_references(message: types.Message, state: FSMContext):
    await state.update_data(references=message.text)
    await message.answer(
        "И последнее: когда вам нужно сдать проект? (Срочно / В течение недели / Не горит)"
    )
    await state.set_state(OrderForm.entering_deadline)

@dp.message(OrderForm.entering_deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    
    user_data = await state.get_data()
    username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"
    
    order_text = (
        f"🔔 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
        f"<b>Услуга:</b> {user_data['service']}\n"
        f"<b>Имя/Ник:</b> {user_data['name']}\n"
        f"<b>Юзернейм клиента:</b> {username}\n"
        f"<b>Описание:</b> {user_data['description']}\n"
        f"<b>Референсы:</b> {user_data['references']}\n"
        f"<b>Сроки:</b> {user_data['deadline']}\n\n"
        f"<i>Заявка для @Qu4rtazz. Свяжитесь с клиентом!</i>"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=order_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")
    
    await message.answer(
        "Спасибо! Ваша заявка отправлена разработчику. Он свяжется с вами в ближайшее время.\n"
        "Чтобы вернуться в начало, нажмите /start"
    )
    await state.clear()

# ==========================================
# ЗАПУСК БОТА
# ==========================================
async def main():
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())