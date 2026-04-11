from django.urls import path
from . import views
from .views import SavingCreateView, SavingDetailView, SavingListView, TargetCreateView, TargetListView, GeneratePDFView

app_name = 'budget'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.HomeTransactionListView.as_view(), name='transaction'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('account/', views.BankAccountCreateView.as_view(), name='account'),
    path('account/create/', views.BankAccountCreateView.as_view(), name='account_create'),
    path('account/update/<int:pk>/', views.BankAccountUpdateView.as_view(), name='account_update'),
    path('account/delete/<int:pk>/', views.BankAccountDeleteView.as_view(), name='account_delete'),
    path('transaction/add/', views.TransactionCreateView.as_view(), name='transaction_add'),
    path('transaction/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('category/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('saving/add/', SavingCreateView.as_view(), name='saving_add'),
    path('saving/<int:pk>/', SavingDetailView.as_view(), name='saving_detail'),
    path('saving/', SavingListView.as_view(), name='saving_list'),
    path('saving/delete/<int:pk>/', views.SavingDeleteView.as_view(), name='saving_delete'),
    path('target/', TargetCreateView.as_view(), name='target'),
    path('target/list/', TargetListView.as_view(), name='target_list'),
    path('target/delete/<int:pk>/', views.TargetDeleteView.as_view(), name='target_delete'),
    path('detail/', views.DetailView.as_view(), name='detail'),
    path('registration-pending/', views.RegistrationPendingView.as_view(), name='registration_pending'),
    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate'),
    path("download-pdf/", GeneratePDFView.as_view(), name="download_pdf"),

]



