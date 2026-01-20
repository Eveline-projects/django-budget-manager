from django.contrib import admin

from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'expense',
        'amount',
        'date'
    )
    list_filter = (
        'user',
        'expense',
    )
    search_fields = ('user', 'expense')
    list_editable = ('user', 'expense')
    ordering = ('-date',)
    date_hierarchy = 'date'

