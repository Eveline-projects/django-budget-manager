from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.ExpenseListView.as_view(), name='expense'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='expense_add'),
    path('expense/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
]