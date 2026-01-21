from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.ExpenseListView.as_view(), name='expense'),
    path('account/', views.BankAccountCreateView.as_view(), name='account'),
    path('account/update/<int:pk>/', views.BankAccountUpdateView.as_view(), name='account_update'),
    path('account/delete/<int:pk>/', views.BankAccountDeleteView.as_view(), name='account_delete'),
]
