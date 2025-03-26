class BalanceManager:
    def __init__(self):
        self.balance = 0  # Основной баланс
        self.reserved_balance = 0  # Зарезервированный баланс

    def deposit(self, amount: int):
        # Пополнить основной баланс.
        if amount < 0:
            raise ValueError("Сумма пополнения не может быть отрицательной.")
        self.balance += amount

    def withdraw(self, amount: int):
        # Снять деньги с основного баланса.
        if amount < 0:
            raise ValueError("Сумма снятия не может быть отрицательной.")
        if self.balance - self.reserved_balance < amount:
            raise ValueError("Недостаточно средств на основном балансе.")
        self.balance -= amount

    def reserve(self, amount: int):
        # Перевести деньги с основного баланса на зарезервированны (заглушка)
        if amount < 0:
            raise ValueError("Сумма резервирования не может быть отрицательной.")
        if self.balance < amount:
            raise ValueError("Недостаточно средств на основном балансе.")
        self.balance -= amount
        self.reserved_balance += amount

    def release(self, amount: int):
        # вернуть деньги с зарезервированного баланса на основной (заглушка)
        if amount < 0:
            raise ValueError("Сумма возврата не может быть отрицательной.")
        if self.reserved_balance < amount:
            raise ValueError("Недостаточно средств на зарезервированном балансе.")
        self.reserved_balance -= amount
        self.balance += amount

    def get_balance(self):
        # текущий баланс.
        return {
            "balance": self.balance,
            "reserved_balance": self.reserved_balance,
        }
