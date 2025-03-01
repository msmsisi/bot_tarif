from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from keyboards.inline import get_main_menu_keyboard
from database.database import Database
from config import DB_FILE

router = Router()
db = Database(DB_FILE)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Здравствуйте! Выберите действие:", reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Выберите действие:", reply_markup=get_main_menu_keyboard())
    await callback.answer()
