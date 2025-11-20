from datetime import date
from decimal import Decimal
from enum import StrEnum, auto
from uuid import uuid4
from typing import Optional

class Category(StrEnum):
    FOOD = auto()
    HOME = auto()
    TRANSPORT = auto()
    ENTERTAINMENT = auto()
    LIFE = auto()
    SHOPPING = auto()
    BILLS = auto()
    INVESTMENTS = auto()


class Expense:
    def __init__(self, amount, category, account_id, description: Optional[str] = ''):
        self.category: Category = category
        self.account_id = account_id
        self.date = date.today()
        self._expense_id = uuid4()
        self.amount: Decimal = amount
        self._save_to_database()
        self.description: Optional[str] = description


    def _save_to_database(self):
        pass


    def modify_expense(self):
        print(self.amount)
        print(self.category)
        print(self.account_id)
        while True:
            print('1. modify expense amount')
            print('2. modify expense category')
            print('3. modify to which account')
            print('4. quit')
            choice = input('which to modify: ')
            try:
                if choice == '1':
                    self.amount = float(input('amount to modify: '))
                if choice == '2':
                    cat_choice = input('category to modify: ').lower()
                    self.category = Category(cat_choice)
                if choice == '3':
                    pass
                if choice == '4':
                    break
            except ValueError as e:
                print(e)


    def __str__(self):
        description_str = f" ({self.description})" if self.description else ""
        return (
            f"Expense ID: {self.expense_id} | Amount: ${self.amount:.2f} | "f"Category: {self.category.value.capitalize()}{description_str} | "f"Paid from Account ID: {self.account_id}")


    @property
    def expense_id(self):
        return self._expense_id


    def get_expense_id(self):
        return self.expense_id

    #TODO zmien expense id na prywanty i automatyczne przyznawanie

wydatek =Expense(100, Category.FOOD, 1)
print(wydatek.get_expense_id())
print(wydatek)
