from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_delivery_info_keyboard, get_main_menu_keyboard, get_delivery_destinations_keyboard
from config import ADMIN_ID, DB_FILE
from database.database import Database

router = Router()
db = Database(DB_FILE)

delivery_conditions = """
Условия заказа / комиссия за услуги:
(организационный сбор)

Нет ограничения по сумме, от 1-упаковок (линией)

До $99 - фиксированная комиссия 600 сом

От $140 - 6% от суммы перевода (не израсходованный остаток - не учитывается)

От $999 - торгуемо (учитывается сложность заказа) 🤝

Выше $1999 - на усмотрение клиента в нижних пределах рыночных цен 🥳

Дополнительно: Сохранность денежных средств и выкупленного товара, до момента сдачи перевозчику (если перевозчик согласован с заказчиком) гарантируется коллективом (команда из более 200 человек) Фэшн Рынок - только в случае перевода / исполнения заказа в рабочем чате заказчика (WhatsApp & Telegram) в присутствии номера wa.me/996500996500, wa.me/996501996501, @marketplacekg, @marketplace_kg

От 10.12.2024 ©️ Лидер команды - Кайрат М.М.
"""

@router.callback_query(F.data == "delivery_info")
async def delivery_info_handler(callback: CallbackQuery) -> None:
    """Обработчик нажатия на кнопку "Информация о доставке"."""
    await callback.message.edit_text("Выберите страну:", reply_markup=get_delivery_info_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("delivery_country_"))
async def delivery_country_handler(callback: CallbackQuery) -> None:
    """Обработчик нажатия на кнопку со страной."""
    country = callback.data.split("_", 2)[2]
    await callback.message.edit_text("Выберите город:", reply_markup=get_delivery_destinations_keyboard(country))
    await callback.answer()

@router.callback_query(F.data.startswith("delivery_city_"))
async def delivery_city_handler(callback: CallbackQuery) -> None:
    """Обработчик нажатия на кнопку с городом."""
    city = callback.data.split("_", 2)[2]
    tariffs = db.get_tariffs_by_city(city)
    if not tariffs:
        await callback.message.edit_text(f"Тарифы для {city} не найдены.")
        return

    message_text = f"В {city}\n\n"  # Изменено: Убрано "ТК ALPHA cargo", "Прайс"
    for tariff_type, delivery_time, cost_per_kg, fixed_cost in tariffs:
        if "add_tariff" in tariff_type:
          continue
        message_text += f"{tariff_type} - 1кг {cost_per_kg}₽\n"
        message_text = message_text.replace(".0", "")  # Удаляем .0 из чисел

        # Добавляем "+3 дня" к сроку доставки, если он меньше 8
        delivery_time_parts = delivery_time.split("-")
        if len(delivery_time_parts) == 1:
          if int(delivery_time) < 8:
            delivery_time = str(int(delivery_time) + 3)
        elif len(delivery_time_parts) == 2:
          if int(delivery_time_parts[0]) < 8 :
            delivery_time = f"{int(delivery_time_parts[0]) + 3}-{int(delivery_time_parts[1]) + 3}"

        message_text += f"\nСроки доставки: {delivery_time} дней\n"
        if fixed_cost:
          message_text += f"Если товар не превышает 10кг. то ставится фиксированная стоимость доставки {int(fixed_cost)}₽"

    await callback.message.edit_text(message_text, reply_markup=get_delivery_info_keyboard())
    await callback.answer()

@router.callback_query(F.data == "back_to_delivery_info")
async def back_to_delivery_info_handler(callback: CallbackQuery) -> None:
    """Обработчик нажатия на кнопку "Назад" к выбору страны."""
    await callback.message.edit_text("Выберите страну:", reply_markup=get_delivery_info_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("delivery_to_"))
async def delivery_to_handler(callback: CallbackQuery) -> None:
    """Обработчик нажатия на кнопку с направлением доставки."""
    country = callback.data.split("_", 2)[2]
    if country == "Условия заказа":
        await callback.message.edit_text(delivery_conditions, reply_markup=get_main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "fulfillment")
async def fulfillment_handler(callback: CallbackQuery) -> None:
    """Обработчик нажатия на кнопку "Фулфилмент"."""
    await callback.message.edit_text("Фулфилмент: https://docs.google.com/spreadsheets/d/1gDCRZgYMpOTdctAuMSz7quEjo4Y6REnqD_jJIhGURB8/edit?usp=sharing", reply_markup=get_main_menu_keyboard())
    await callback.answer()

@router.message(F.text.startswith("/delete_delivery"))
async def delete_delivery_handler(message: Message) -> None:
    """Обработчик команды /delete_delivery."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    try:
        _, city_to_delete = message.text.split(maxsplit=1)

        db.cursor.execute("SELECT city FROM delivery WHERE city=?", (city_to_delete,))
        result = db.cursor.fetchone()
        if result:
            city_to_delete = result[0]
            db.delete_delivery_tariff("Россия", city_to_delete)
            await message.answer(f"Тариф для {city_to_delete} успешно удален.")
        else:
            await message.answer(f"Тариф для {city_to_delete} не найден, либо уже был удален.")
    except (ValueError, TypeError):
        await message.answer("Неверный формат команды. Пример: /delete_delivery [город].")

@router.message(F.text.startswith("/add_tariff"))
async def add_tariff_handler(message: Message) -> None:
    """Обработчик команды /add_tariff."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    if message.text == "/add_tariff":
        await message.answer("""Введите данные в следующем формате:
[Город]
Тип
[Тип товара]
Срок доставки: [Срок доставки]
Стоимость за кг: [Стоимость]
Пример:
Москва
Тип
Пошив
Срок доставки: 5
Стоимость за кг: 50""") # Изменено: Убрано "Фиксированная стоимость"
        return

    lines = message.text.strip().split('\n')
    if len(lines) != 5 or lines[1] != "Тип" or not lines[3].startswith("Срок доставки:") or not lines[4].startswith("Стоимость за кг:"):
        await message.answer("""Неверный формат ввода. Введите данные в следующем формате:
Пример:
Москва
Тип
Пошив
Срок доставки: 5
Стоимость за кг: 50""") # Изменено: Убрано "Фиксированная стоимость"
        return

    try:
        city = lines[0]
        tariff_type = lines[2]
        delivery_time = lines[3].split(": ")[1]
        cost_per_kg = float(lines[4].split(": ")[1].replace("₽", ""))
        fixed_cost = 1060 # Фиксированная стоимость 1060

        if int(delivery_time) < 8 and "-" not in delivery_time:
            delivery_time = f"{delivery_time}-{int(delivery_time) + 3}"
        elif "-" in delivery_time:
            delivery_time_parts = delivery_time.split("-")
            if int(delivery_time_parts[0]) < 8 :
              delivery_time = f"{int(delivery_time_parts[0]) + 3}-{int(delivery_time_parts[1]) + 3}"
        
        db.add_delivery_tariff("Россия", city, tariff_type, delivery_time, cost_per_kg, fixed_cost)

        if db.cursor.rowcount > 0:
          await message.answer(f"Тариф для {city} с типом {tariff_type} успешно обновлен.")
        else:
          await message.answer(f"Тариф для {city} с типом {tariff_type} успешно добавлен.")

    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении/обновлении тарифа: {e}")
