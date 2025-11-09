from datetime import date
from bank_accounts import BankAccount
from typing import List, Dict, Any


class User:
    """Represents a user of the financial system."""

    def __init__(self, user_id: int, user_type: str, username: str):

        self.user_id = user_id
        self.user_type = user_type
        self.username = username

        self.accounts: List[BankAccount] = []
        self.expenses: List[Dict[str, Any]] = []

    def add_account(self, account: BankAccount):
        """Adds a BankAccount object to the user's list of accounts."""

        if any(acc.account_id == account.account_id for acc in self.accounts):
            print(f"Account ID: {account.account_id} is already assigned to user {self.username}.")
            return

        if account.user_id != self.user_id:
            print(
                f"Error: Account ID: {account.account_id} is for User ID {account.user_id}, not {self.username} (ID: {self.user_id}).")
            return

        self.accounts.append(account)
        print(f"Account '{account.account_type}' (ID: {account.account_id}) has been added to user {self.username}.")

    def add_expense(self, amount: float, category: str, description: Optional[str] = None):
        """Adds an expense and attempts to cover it from an active account."""

        if amount <= 0:
            print("The amount must be greater than zero.")
            return

        assigned_account = None

        # Try to find an active account with sufficient balance to cover the expense
        # TODO will be resolved with jira item JPYD92-20
        for account in self.accounts:
            if account.is_active and account.withdraw(amount):
                assigned_account = account
                break

        if assigned_account is None:
            print("Error: No active account found with sufficient funds to cover this expense.")
            return

        # Create expense record
        expense = {
            "amount": amount,
            "category": category,
            "description": description,
            "account_id": assigned_account.account_id,
            "expense_id": len(self.expenses) + 1  # Simple ID generation
        }

        self.expenses.append(expense)
        assigned_account.add_expense_id(expense["expense_id"])
        print(
            f"Expense {amount:.2f} PLN in category '{category}' successfully paid from account ID: {assigned_account.account_id}.")

    def show_accounts(self):
        """Displays details for all bank accounts assigned to the user."""

        if not self.accounts:
            print(f"User {self.username} has no accounts assigned.")
            return

        print(f"\n--- Bank Accounts for {self.username} (ID: {self.user_id}) ---")
        for account in self.accounts:
            print("---------------------------------------")
            print(account)
        print("---------------------------------------")

    def show_expenses(self):
        """Displays the user's list of expenses."""

        if not self.expenses:
            print(f"User {self.username} has no expenses.")
            return

        print(f"\n--- Expenses for {self.username} ---")
        for expense in self.expenses:
            print(
                f"Expense ID: {expense['expense_id']} | Amount: {expense['amount']:.2f} PLN | Category: {expense['category']} | Paid from Account ID: {expense['account_id']}")
            if expense['description']:
                print(f"    Description: {expense['description']}")
        print("---------------------------------------")


# ----------------------------------------------------
## Example Usage: Creating a User and a BankAccount
# ----------------------------------------------------

# Added: if __name__ == "__main__": block
if __name__ == "__main__":
    # 1. Define user and account IDs
    USER_ID_A = 101
    ACCOUNT_ID_MAIN = 5001

    # 2. Create one user
    user_basia = User(
        user_id=USER_ID_A,
        user_type="Adult",
        username="Basia Kowalska"
    )

    # 3. Create one bank account for the user
    basia_main_account = BankAccount(
        account_id=ACCOUNT_ID_MAIN,
        user_id=USER_ID_A,
        account_type="Checking",
        initial_balance=1500.00
    )

    # 4. Create a second account (for demonstration)
    basia_savings_account = BankAccount(
        account_id=5002,
        user_id=USER_ID_A,
        account_type="Savings",
        initial_balance=500.00
    )

    # 5. Add accounts to the user
    print("\n### ADDING ACCOUNTS ###")
    user_basia.add_account(basia_main_account)
    user_basia.add_account(basia_savings_account)

    # 6. Show initial accounts status
    user_basia.show_accounts()

    # 7. Add expenses
    print("\n### ADDING EXPENSES ###")
    user_basia.add_expense(55.50, "Groceries", "Weekly shopping")
    basia_savings_account.deposit(200.00)
    user_basia.add_expense(100.00, "Bills", "Electricity bill")
    user_basia.add_expense(20.00, "Transport", "Bus ticket")

    # 8. Show expenses
    user_basia.show_expenses()

    # 9. Show final accounts status (to verify balances and expense assignments)
    user_basia.show_accounts()
