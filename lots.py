# Пока под вопросом этот модуль


from config import DATA_BASE


class Lot:

    DATA_BASE = DATA_BASE

    def __init__(self, id: int, name: str, text: str, images: tuple[str], seller: str, tags: tuple[str]) -> None:

        self._id = id
        self._name = name
        self._text = text
        self._images = images
        self._seller = seller
        self._tags = tags
    