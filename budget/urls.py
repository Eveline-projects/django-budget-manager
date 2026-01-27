from django.urls import path
from . import views
from .views import SavingCreateView

app_name = 'budget'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.ExpenseListView.as_view(), name='expense'),
    path('account/', views.BankAccountCreateView.as_view(), name='account'),
    path('account/create/', views.BankAccountCreateView.as_view(), name='account_create'),
    path('account/update/<int:pk>/', views.BankAccountUpdateView.as_view(), name='account_update'),
    path('account/delete/<int:pk>/', views.BankAccountDeleteView.as_view(), name='account_delete'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='expense_add'),
    path('expense/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('category/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('expense/saving', SavingCreateView.as_view(), name='saving'),
]
