from datetime import date

class User:



    def __init__(self, user_type: str, username: str):
  
        self.user_type = user_type
        self.username = username
        self.accounts = []       # list of assigned accounts
        self.expenses = []       # list of expenses made by the user


    def add_account(self, account_name: str):

        if account_name not in self.accounts:
            self.accounts.append(account_name)
            print(f"Account '{account_name}' has been added to user {self.username}.")
        else:
            print(f"Account '{account_name}' already exists.")


    def add_expense(self, amount: float, category: str, description: str = ""):
    
        if amount <= 0:
            print("The amount must be greater than zero.")
            return

        expense = {
            "amount": amount,
            "category": category,
            "description": description
        }

        self.expenses.append(expense)
        print(f"Expense {amount:.2f} PLN in category '{category}' added for user {self.username}.")


    def show_accounts(self):
        
        if not self.accounts:
            print(f"User {self.username} has no accounts.")
            return

        print(f"\nAccounts for {self.username}:")
        for account in self.accounts:
            print(f"- {account}")


    def show_expenses(self):
          
        if not self.expenses:
            print(f"User {self.username} has no expenses.")
            return

        print(f"\nExpenses for {self.username}:")
        for i, expense in enumerate(self.expenses, start=1):
            print(f"{i}. {expense['amount']} PLN - {expense['category']} ({expense['description']})")


# Example usage 
if __name__ == "__main__":
   
    user1 = User("adult", "Agnieszka")

  
    user1.add_account("Joint Account")
    user1.add_account("Savings Account")

    # Add expenses
    user1.add_expense(120.50, "Groceries", "Lidl")
    user1.add_expense(300.00, "Transport", "Monthly pass")

    # Show results
    user1.show_accounts()
    user1.show_expenses()