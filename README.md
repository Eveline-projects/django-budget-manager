# Personal Budget Manager – Django Web Application

Personal Budget Manager is a web application built with Python and Django that allows users to manage their personal finances in one place.

The app includes features for managing bank accounts, adding income and expenses, and viewing a dashboard with overall balance and recent transactions. It was created as a team project during the InfoShare Academy bootcamp to learn Django, Git-based collaboration, and best practices for web application development.

## Features

- User authentication: registration and login for secure access
- Bank account management: create, edit, and delete bank accounts
- Transaction management: add income and expenses with categories
- Dashboard: view overall balance and recent transactions
- Expense categories: e.g. food, bills, entertainment
- Responsive UI: clean and user-friendly interface built with Bootstrap

## Technologies

### Backend

- Python
- Django
- Django ORM

### Frontend

- HTML5
- CSS
- Bootstrap

### Database

- SQLite

### Other

- Git (collaborative development workflow)
- InfoShare Academy bootcamp project

## My Responsibilities

As part of the team, I was responsible for:

- Implementing the logic for adding expenses and displaying the balance on the dashboard
- Building the account management module (create, edit, delete bank accounts)
- Integrating user authentication and authorization using Django’s built-in system
- Collaborating with teammates on feature planning, code reviews, and UI improvements

## How to Run the Project

1. Clone the repository:

   ```bash
   git clone https://github.com/Eveline-projects/django-budget-manager.git
   cd django-budget-manager
   ```

2. Create and activate a virtual environment (example with `venv`):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations and run the development server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Open the app in your browser:

   - Web app: http://127.0.0.1:8000/

## Project Status

This project was created for educational purposes during the InfoShare Academy bootcamp.  
The repository is kept public as part of my learning journey and portfolio for Django and Python development.

## Team

- Ewelina Kaczmarek
- Katarzyna Marchewka
- Piotr Kubski
