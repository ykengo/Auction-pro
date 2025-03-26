import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.token import TokenValidationError
from balance import BalanceManager
from config import TOKEN
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

#Менеджер баланса
balance_manager = BalanceManager()

class BalanceStates(StatesGroup):
    AWAITING_DEPOSIT = State()
    AWAITING_WITHDRAW = State()
    AWAITING_RESERVE = State()
    AWAITING_RELEASE = State()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Баланс"),
            KeyboardButton(text="Доступные лоты"),
        ],
        [
            KeyboardButton(text="Мои лоты"),
            KeyboardButton(text="Создание лота"),
        ]
    ],
    resize_keyboard=True
)

# Кнопка возврата
back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]],
    resize_keyboard=True
)


# /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в главное меню!", reply_markup=main_menu)




@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в главное меню!", reply_markup=main_menu)

# Меню (кроме баланса)

@router.message(lambda message: message.text == "Доступные лоты")
async def show_available_lots(message: types.Message):
    await message.answer("Здесь будет список доступных лотов", reply_markup=back_button)

@router.message(lambda message: message.text == "Мои лоты")
async def show_my_lots(message: types.Message):
    await message.answer("Здесь будет список ваших лотов", reply_markup=back_button)

@router.message(lambda message: message.text == "Создание лота")
async def create_lot(message: types.Message):
    await message.answer("Здесь будет форма создания лота", reply_markup=back_button)


# Баланс
@router.message(lambda message: message.text == "Баланс")
async def show_balance_menu(message: types.Message):
    balance_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Текущий баланс")],
            [KeyboardButton(text="Пополнить баланс")],
            [KeyboardButton(text="Снять деньги")],
            [KeyboardButton(text="Зарезервировать деньги")],
            [KeyboardButton(text="Вернуть деньги из резерва")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие с балансом:", reply_markup=balance_menu)

# Текущий баланс
@router.message(lambda message: message.text == "Текущий баланс")
async def show_current_balance(message: types.Message):
    balance = balance_manager.get_balance()
    await message.answer(
        f"Ваш баланс:\n"
        f"Основной: {balance['balance']} ₽\n"
        f"Зарезервированный: {balance['reserved_balance']} ₽"
    )

# Пополнение баланса
@router.message(lambda message: message.text == "Пополнить баланс")
async def deposit_balance(message: types.Message, state: FSMContext):
    await state.set_state(BalanceStates.AWAITING_DEPOSIT)
    await message.answer("Введите сумму для пополнения (целое число):", reply_markup=types.ReplyKeyboardRemove())

@router.message(BalanceStates.AWAITING_DEPOSIT)
async def process_deposit(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        balance_manager.deposit(amount)
        balance = balance_manager.get_balance()
        await message.answer(
            f"✅ Баланс успешно пополнен на {amount} ₽\n"
            f"Новый баланс: {balance['balance']} ₽",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}\nПопробуйте снова:")

# Снятие денег
@router.message(lambda message: message.text == "Снять деньги")
async def withdraw_balance(message: types.Message, state: FSMContext):
    await state.set_state(BalanceStates.AWAITING_WITHDRAW)
    await message.answer("Введите сумму для снятия (целое число):", reply_markup=types.ReplyKeyboardRemove())

@router.message(BalanceStates.AWAITING_WITHDRAW)
async def process_withdraw(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        balance_manager.withdraw(amount)
        balance = balance_manager.get_balance()
        await message.answer(
            f"Успешно снято {amount}\n"
            f"Новый баланс: {balance['balance']} ₽",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}\nПопробуйте снова:")

# Резервирования денег (должно происходить автоматически, пока заглушка)
@router.message(lambda message: message.text == "Зарезервировать деньги")
async def reserve_balance(message: types.Message, state: FSMContext):
    await state.set_state(BalanceStates.AWAITING_RESERVE)
    await message.answer("Введите сумму для резервирования (целое число):", reply_markup=types.ReplyKeyboardRemove())

@router.message(BalanceStates.AWAITING_RESERVE)
async def process_reserve(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        balance_manager.reserve(amount)
        balance = balance_manager.get_balance()
        await message.answer(
            f"Успешно зарезервировано {amount} ₽\n"
            f"Основной баланс: {balance['balance']} ₽\n"
            f"Зарезервированный: {balance['reserved_balance']} ₽",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}\nПопробуйте снова:")

# Возврата денег из резерва
@router.message(lambda message: message.text == "Вернуть деньги из резерва")
async def release_balance(message: types.Message, state: FSMContext):
    await state.set_state(BalanceStates.AWAITING_RELEASE)
    await message.answer("Введите сумму для возврата из резерва (целое число):", reply_markup=types.ReplyKeyboardRemove())

@router.message(BalanceStates.AWAITING_RELEASE)
async def process_release(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        balance_manager.release(amount)
        balance = balance_manager.get_balance()
        await message.answer(
            f"Успешно возвращено {amount} из резерва\n"
            f"Основной баланс: {balance['balance']} ₽\n"
            f"Зарезервированный: {balance['reserved_balance']} ₽",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}\nПопробуйте снова:")

# Возврат
@router.message(lambda message: message.text == "Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню", reply_markup=main_menu)


# Запуск бота
async def main():
    try:
        await dp.start_polling(bot)
    except TokenValidationError:
        print("Ошибка: Неверный токен бота!")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
