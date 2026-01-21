from django.contrib import admin

from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        # 'user',
         'category',
        'amount',
        'date'
    )
    # list_filter = (
    #     # 'user',
    #     'expense',
    # )
    search_fields = ( 'amount','category')
    # list_editable = ( 'category',)
    ordering = ('-date',)
    date_hierarchy = 'date'

    # search_fields = ('user', 'expense')
    # list_editable = ('user', 'expense')

