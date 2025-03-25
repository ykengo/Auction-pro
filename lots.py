from re import fullmatch
from datetime import datetime
from sqlite3 import connect

from aiogram.types import PhotoSize, FSInputFile, ReplyKeyboardMarkup, KeyboardButton

from config import DATA_BASE


class Lot:

    """Класс для описания лота"""

    def __init__(self, _id: int, seller: str, buyer: str, name: str, text: str, path_to_images: str, start_price: int, max_price: int, step: int, start_date: str, end_date: str) -> None:

        self._id = _id
        self._name = name
        self._text = text
        self._path_to_images = path_to_images
        self._seller = seller
        self._buyer = buyer
# self._tags = tags
        self._start_date = start_date
        self._end_date = end_date
# self._is_active = is_active
        self._start_price = start_price
        self._max_price = max_price
        self._step = step

    @staticmethod
    def valid_name(name: str) -> bool:

        if type(name) is not str:

            return False

        return True

    @staticmethod
    def valid_text(text: str) -> bool:

        if type(text) is not str:

            return False

        return True

    @staticmethod
    def valid_images(images: list[PhotoSize]) -> bool:

        for image in images:

            if type(image) is not PhotoSize:

                return False

        return True

    @staticmethod
    def valid_date(date: str) -> bool:

        if not fullmatch(r'\d{4}-\d{2}-\d{2}', date):

            return False

        try:

            if len(date.split('-')[1]) != 2 or len(date.split('-')[2]) != 2:

                return False
            
            if not Lot.is_future_date(date):

                return False

            return True

        except (ValueError, TypeError):

            return False
        
    @staticmethod
    def is_future_date(date: str) -> bool:  # Проверяет, что дата позже нынешней даты
        
        try:
            
            year, month, day = map(int, date.split('-'))
            input_date = datetime(year=year, month=month, day=day).date()
            current_date = datetime.now().date()

            return input_date > current_date
        
        except (ValueError, TypeError, AttributeError):
            
            return False

    @staticmethod
    def valid_price(price: int) -> bool:

        if type(price) is not int or price < 1:

            return False

        return True

    @staticmethod
    def valid_step(step: int) -> bool:

        if type(step) is not int or step < 1:

            return False

        return True

    @property
    def buyer(self) -> str:

        return self._buyer

    @buyer.setter
    def buyer(self, buyer: str) -> None:

        if type(buyer) is not str:

            return

        self._buyer = buyer

    # @property  # Под вопросом
    # def is_active(self) -> bool:
    #
    #     return self._is_active
    #
    # @is_active.setter
    # def is_active(self, is_active: bool) -> None:
    #
    #     if type(self._is_active) is not bool:
    #
    #         return
    #
    #     self._is_active = is_active

    @property
    def max_price(self) -> int:

        return self._max_price

    @max_price.setter
    def max_price(self, max_price: int) -> None:

        if type(max_price) is not max_price or max_price <= self._max_price:

            return

        self._max_price = max_price

    def get_send_lot(self) -> tuple[FSInputFile, str]:

        """Создание оболочки лота"""

        photo = FSInputFile(self._path_to_images)
        caption = f'''ID Лота: {self._id}
ID Продавца: {self._seller}
Название: {self._name}
Описание: {self._text}
Дата начала: {self._start_date}
Дата конца: {self._end_date}
ID покупателя: {self.buyer if self.buyer is not None else 'Пока никого'}
Начальная ставка: {self._start_price}
Текущая ставка: {self.max_price if self.max_price else 'Пока нету'}
Шаг: {self._step}
''' #Теги: {self._tags}
    #Статус: {'Активно' if self.is_active else 'Не активно'}
        return photo, caption


def create_lot_by_id(_id: int) -> Lot:

    """Создание лота"""

    if _id <= 0:

        raise ValueError('Указан не тот ID')

    with connect(DATA_BASE) as con:

        result = con.cursor().execute(f'''SELECT * FROM Lots
                                          WHERE id = {_id}''').fetchall()

    return Lot(*result[0])

def get_on_all_lots_keyboard() -> ReplyKeyboardMarkup:

    """Создание клавиатуры для просмотра лотов"""

    cancel_lot = KeyboardButton(text='Выйти из просмотра лотов')
    subscription_lot = KeyboardButton(text='Подписаться на лот')
    up_price_lot = KeyboardButton(text='Повысить ставку на лот')
    next_lot = KeyboardButton(text='Следующий лот')

    markup = ReplyKeyboardMarkup(keyboard=[[cancel_lot], [subscription_lot], [up_price_lot], [next_lot]])
    return markup
