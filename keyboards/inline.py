from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from config import DB_FILE
db = Database(DB_FILE)

def get_main_menu_keyboard():
    """Создает клавиатуру главного меню."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Курс валют", callback_data="currency_rates"),
            InlineKeyboardButton(text="Калькулятор", callback_data="calculator"),
        ],
        [
            InlineKeyboardButton(text="Информация о доставке", callback_data="delivery_info"),
        ],
        [
            InlineKeyboardButton(text="Условия заказа", callback_data="delivery_to_Условия заказа"),
            InlineKeyboardButton(text="ССЫЛКА НА ФФ", callback_data="fulfillment")
        ]
    ])
    return keyboard

def get_currency_rates_keyboard():
    """Создает клавиатуру для раздела курсов валют."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Обновить", callback_data="update_currency")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
        ]
    ])
    return keyboard

def get_delivery_info_keyboard():
  keyboard = InlineKeyboardMarkup(inline_keyboard=[])
  countries = db.get_all_delivery_countries()

  if not countries:
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")])
    return keyboard
  
  for country in countries:
    keyboard.inline_keyboard.append([InlineKeyboardButton(text=country, callback_data=f"delivery_country_{country}")])

  keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")])
  return keyboard

def get_delivery_destinations_keyboard(country):
    """Создает клавиатуру с направлениями доставки для выбранной страны."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    cities = db.get_all_delivery_cities_by_country(country)
    
    if not cities:
      keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_delivery_info")])
      return keyboard

    for city in cities:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=city, callback_data=f"delivery_city_{city}")])
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_delivery_info")])
    return keyboard
