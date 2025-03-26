# Модуль для обработки апдейтов от пользователя
import os
from sqlite3 import connect

from config import DATA_BASE, DOWNLOADS_USERS_LOT
from utils.button_text import ButtonText
from utils.state_machine import StateCreateLot, StateAllLots
from lots import Lot, create_lot_by_id, get_on_all_lots_keyboard

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


router = Router()

# Для создания лотов надо добавить валидатор получаемых данных
@router.message(F.text == ButtonText.CREATE_LOT)
@router.message(Command(commands=['create_lot']))
async def process_create_lot_command(message: Message, state: FSMContext) -> None:

    """Создание лота и переход в другие состояния"""

    await message.answer('Введите название для лота')
    await state.set_state(StateCreateLot.NAME_LOT)


@router.message(StateCreateLot.NAME_LOT)
async def process_adding_name_lot(message: Message, state: FSMContext) -> None:

    if not Lot.valid_name(message.text):

        await message.answer('Неправильный формат название')
        await message.answer('Попробуйте снова')
        return None

    await state.update_data(name_lot=message.text)
    await message.answer('Введите описание для вашего лота')
    await state.set_state(StateCreateLot.TEXT_LOT)


@router.message(StateCreateLot.TEXT_LOT)
async def process_adding_text_lot(message: Message, state: FSMContext) -> None:

    if not Lot.valid_text(message.text):

        await message.answer('Неправильный формат описания')
        await message.answer('Попробуйте снова')
        return None

    await state.update_data(text_lot=message.text)
    await message.answer('Введите изображения лота')
    await state.set_state(StateCreateLot.IMAGES_LOT)


@router.message(StateCreateLot.IMAGES_LOT)
async def process_adding_images_lot(message: Message, state: FSMContext) -> None:

    if not Lot.valid_images(message.photo):

        await message.answer('Неправильный формат изображения')
        await message.answer('Попробуйте снова')
        return None

    image = message.photo[-1]
    image_file = await message.bot.get_file(image.file_id)

    os.makedirs(DOWNLOADS_USERS_LOT, exist_ok=True)

    image_path = image_file.file_path
    image_system_path_lot = os.path.join(DOWNLOADS_USERS_LOT, f'photo_{message.message_id}.jpg')
    await message.bot.download_file(image_path, image_system_path_lot)

    await state.update_data(image_path_lot=image_system_path_lot)
    await message.answer('Введите дату начала и конца лота в формате (год-месяц-день)')
    await state.set_state(StateCreateLot.DATE_LOT)


@router.message(StateCreateLot.DATE_LOT)
async def process_adding_date_lot(message: Message, state: FSMContext) -> None:

    try:

        start_date_lot, end_date_lot = message.text.split(' ')

    except ValueError:

        await message.answer('Вы не ввели две даты')
        await message.answer('Попробуйте снова')
        return None

    if not Lot.valid_date(start_date_lot) or not Lot.valid_date(end_date_lot):

        await message.answer('Неправильный формат даты')
        await message.answer('Попробуйте снова')
        return None

    await state.update_data(start_date_lot=start_date_lot, end_date_lot=end_date_lot)
    await message.answer('Введите начальную ставку лота')
    await state.set_state(StateCreateLot.START_PRICE)

@router.message(StateCreateLot.START_PRICE)
async def process_adding_start_price_lot(message: Message, state: FSMContext) -> None:

    try:

        if not Lot.valid_price(int(message.text)):

            await message.answer('Неправильный формат ставки')
            await message.answer('Попробуйте снова')
            return None

    except ValueError:

        await message.answer('Вы ввели не целое число')
        await message.answer('Попробуйте снова')

    await state.update_data(start_price_lot=int(message.text))
    await message.answer('Введите шаг ставки лота')
    await state.set_state(StateCreateLot.STEP)


@router.message(StateCreateLot.STEP)
async def process_adding_step_price_lot(message: Message, state: FSMContext) -> None:

    try:

        if not Lot.valid_step(int(message.text)):

            await message.answer('Неправильный формат шага ставки')
            await message.answer('Попробуйте снова')
            return None

    except ValueError:

        await message.answer('Вы ввели не целое число')
        await message.answer('Попробуйте снова')

    await state.update_data(step_price_lot=int(message.text))
    await message.answer('Ваш лот будет добавлен в аукцион')
    data = await state.get_data()

    with connect(DATA_BASE) as con:

        con.cursor().execute(f'''INSERT INTO Lots(owner_id, buyer_id, name, description, picture_path, cur_price, max_price, step, time_start, time_end)
                                 VALUES({message.from_user.id}, null, '{data['name_lot']}', '{data['text_lot']}',
                                        '{data['image_path_lot']}', {data['start_price_lot']}, null, {data['step_price_lot']}, 
                                        '{data['start_date_lot']}', '{data['end_date_lot']}')''')
    await state.clear()


@router.message(F.text == ButtonText.ALL_LOTS)
@router.message(Command(commands=['all_lots']))
async def process_all_lots(message: Message, state: FSMContext) -> None:

    await message.answer('Вы вошли в режим просмотра лотов')
    await message.answer('Чтобы выйти из режима просмотра лотов напишите: "cancel"')
    await state.set_state(StateAllLots.WATCHING)

    lot = create_lot_by_id(1)
    photo, caption = lot.get_send_lot()
    markup = get_on_all_lots_keyboard()
    await state.update_data(id=2)
    await message.bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption, reply_markup=markup)


@router.message(F.text == ButtonText.NEXT_LOT)
@router.message(StateAllLots.WATCHING)
async def process_watching_lot(message: Message, state: FSMContext) -> None:

    if message.text == 'cancel':

        await state.clear()
        await message.answer('Вы вышли из режима просмотра лотов')
        return None

    data = await state.get_data()
    _id = data['id']
    lot = create_lot_by_id(_id)
    photo, caption = lot.get_send_lot()
    markup = get_on_all_lots_keyboard()
    await state.update_data(id=_id + 1)
    await message.bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption, reply_markup=markup)