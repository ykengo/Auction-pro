# Модуль для описания машин состояния пользователей


from aiogram.fsm.state import State, StatesGroup


class StateCreateLot(StatesGroup):

    """Класс для описания поведения ТГ бота в момент создания лота"""

    NAME_LOT = State()  # Название лота
    TEXT_LOT = State()  # Описание лота
    IMAGES_LOT = State()  # Изображения лота
#   TAGS_LOT = State()  # Теги лота (Пока под вопросом)
    DATE_LOT = State()  # Дата начала и конца лота
    START_PRICE = State()
    STEP = State()

class StateAllLots(StatesGroup):

    """Класс для описания поведения ТГ бота в момент просмотра лотов пользователей"""

    WATCHING = State()  # В категории просматривает

