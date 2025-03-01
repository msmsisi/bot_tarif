from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_currency_rates_keyboard
from database.database import Database
from config import DB_FILE, ADMIN_ID

router = Router()
db = Database(DB_FILE)

# ... (остальной код без изменений)

@router.message(F.text.startswith("/update"))
async def update_currency_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    try:
        _, currency, rate = message.text.split()
        rate = float(rate)
        db.update_currency_rate(currency, rate)
        await message.answer(f"Курс {currency} обновлен до {rate}")
    except (ValueError, TypeError):
        await message.answer("Неверный формат команды. Пример: /update USD 89.5")
# ... (остальной код без изменений)
