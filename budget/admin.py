from django.contrib import admin

from .models import Transaction, Category


@admin.register(Transaction)
class transactionAdmin(admin.ModelAdmin):
    list_display = (
        # 'user',
         'category',
        'amount',
        'date'
    )
    # list_filter = (
    #     # 'user',
    #     'transaction',
    # )
    search_fields = ( 'amount','category')
    # list_editable = ( 'category',)
    ordering = ('-date',)
    date_hierarchy = 'date'

    # search_fields = ('user', 'transaction')
    # list_editable = ('user', 'transaction')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
