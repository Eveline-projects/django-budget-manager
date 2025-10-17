from datetime import date
from typing import List


class BankAccount:
    def __init__(self, account_id: int, user_id: int, account_type: str,
                 initial_balance: float = 100.0, is_active: bool = True ):
        self.account_id = account_id
        self.user_id = user_id
        self.account_type = account_type
        self.balance = initial_balance
        self.is_active = is_active

        self.assigned_expense_ids: List[int] = []

        self._creation_date: date = date.today()


    def deposit(self, amount: float) -> bool:
        if self.is_active and amount > 0:
            self.balance += amount
            print(f"Deposit of ${amount:.2f} successful. New balance: $ {self.balance:.2f}.")
            return True
        return False


    def withdraw(self, amount: float) -> bool:
        if self.is_active and 0 < amount <= self.balance:
            self.balance -= amount
            print(f"Withdraw of {amount:.2f} PLN successful. New balance: {self.balance:.2f} PLN.")
            return True
        return False


    def add_expense_id(self, expense_id: int):
        if expense_id not in self.assigned_expense_ids:
            self.assigned_expense_ids.append(expense_id)
            print(f"Expense added to account")
            return True
        return False


    def get_creation_date(self) -> date:
        return self._creation_date


    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return (f"Account ID: {self.account_id}, Type: {self.account_type}({status})\n"
                f" Balance: {self.balance:.2f}, "
                f" Created: {self._creation_date}\n"
                f' Expenses Count: {len(self.assigned_expense_ids)}')


basia = BankAccount(1,2,'3')
print(basia.withdraw(100))

