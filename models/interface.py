from .expenses import Expense
from .bank_accounts import BankAccount
from .users import User

class Interface:
    def __init__(self):
        self.all_users = {}
        self.all_bank_accounts = {}
        self.all_expenses = {}

        self.next_expense_id = 1
        self.next_account_id = 1
        self.current_user_id = 1

        self.categories = Expense.CATEGORIES
        self.CATEGORY_START_INDEX = 5

        self.setup_initial_data()

    def setup_initial_data(self):
        checking_account = BankAccount(
            account_id = self.next_account_id,
            user_id = self.current_user_id,
            account_type = 'Checking',
            initial_balance = 1500.00,
        )
        self.all_bank_accounts[self.next_account_id] = checking_account
        self.next_account_id += 1

    @staticmethod
    def display_main_menu():
        print('\n' + '='*50)
        print('               HOME BUDGET MANAGER MENU')
        print('='*50)
        print('1. Current Financial Overview (Balance, Savings, Goals)')
        print('2. Add New Expense')
        print('3. View Detailed Expense List')
        print('4. View Statistics and Summaries')
        print('-'*50)
        print('0. Exit Application')
        print('='*50)

    def handle_menu_selection(self):
        while True:
            self.display_main_menu()
            max_choice = self.CATEGORY_START_INDEX + len(self.categories) - 1
            choice = input(f'Enter your choice (0 - {max_choice}): ').strip()
            choice = int(choice)
            if choice == 0:
                break
            elif choice == 1:
                self.view_financial_overview_interface()
            elif choice == 2:
                self.add_new_expenses_interface()
            elif choice == 3:
                pass
            elif choice == 4:
                while True:
                    print('\n' + '=' * 50)
                    print('               CATEGORIES')
                    print('=' * 50)
                    print('1. Food')
                    print('2. Home')
                    print('3. Transport')
                    print('4. Entertainment')
                    print('5. Life')
                    print('6. Shopping')
                    print('7. Bills')
                    print('8. Investments')
                    print('-' * 50)
                    print('0. Return')
                    print('=' * 50)
                    new_choice = input('Enter your choice: ')
                    if new_choice == 1:
                        pass
                    if new_choice == 2:
                        pass
                    if new_choice == 3:
                        pass
                    if new_choice == 4:
                        pass
                    if new_choice == 5:
                        pass
                    if new_choice == 6:
                        pass
                    if new_choice == 7:
                        pass
                    if new_choice == 8:
                        pass
                    else:
                        break

    def add_new_expenses_interface(self):
        print(self.categories)
        cat = input('Select category: ').capitalize()
        amount = 0
        if cat in self.categories:
            try:
                amount = float(input('Insert the amount you want to add: '))
            except ValueError as e:
                print(e)
            desc = input('Add a description: ')
            expense = User('sdaad', 'asdas')
            expense.add_expense(amount, cat, desc)

    def view_financial_overview_interface(self):
        pass



