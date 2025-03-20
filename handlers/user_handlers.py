# Модуль для обработки апдейтов от пользователя


from utils.button_text import ButtonText
from utils.state_machine import StateCreateLot

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


router = Router()

# Для создания лотов надо добавить валидатор получаймых данных
@router.message(F.text == ButtonText.CREATE_LOT)
@router.message(Command(commands=['create_lot']))
async def process_create_lot_command(message: Message, state: FSMContext) -> None:

    '''Создание лота и переход в другие состояния'''

    await message.answer('Введите название для лота')
    await state.set_state(StateCreateLot.NAME_LOT)


@router.message(StateCreateLot.NAME_LOT)
async def process_adding_name_lot(message: Message, state: FSMContext) -> None:

    await state.update_data(name_lot=message.text)
    await message.answer('Введите описание для вашего лота')
    await state.set_state(StateCreateLot.TEXT_LOT)

@router.message(StateCreateLot.TEXT_LOT)
async def process_adding_text_lot(message: Message, state: FSMContext) -> None:

    await state.update_data(text_lot=message.text)
    await message.answer('Введите изображения лота')
    await state.set_state(StateCreateLot.IMAGES_LOT)


@router.message(StateCreateLot.IMAGES_LOT)
async def process_adding_images_lot(message: Message, state: FSMContext) -> None:

    await state.update_data(images_lot=message.photo)
    await message.answer('Введите дату начала и конца лота в формате (день:месяц:год)')
    await state.set_state(StateCreateLot.DATE_LOT)


@router.message(StateCreateLot.DATE_LOT)
async def process_adding_date_lot(message: Message, state: FSMContext) -> None:

    start_date_lot, end_date_lot = message.text.split(' ')

    await state.update_data(start_date_lot=start_date_lot, end_date_lot=end_date_lot)
    await message.answer('Ваш лот будет добавлен в аукцион')
    await state.clear()  # Пока добавление в базу данных не происходит и данные просто очищаются


