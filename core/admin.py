from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from utils.helper import FormatError, card_mask, clean_balance, format_card, format_expire, format_phone, prepare_message, send_message
from core.models import Card
from decimal import Decimal
# Register your models here.

class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        import_id_fields = ['card_number']
        fields = ['card_number', 'expire', 'phone', 'status', 'balance']
        export_order = ['card_number', 'expire', 'phone', 'status', 'balance']

    def before_import_row(self, row, **kwargs):
        try:
            card_number = card_mask(format_card(row.get("card_number")))
            phone = format_phone(row.get("phone"))
            expire = format_expire(row.get("expire"))    
            row["card_number"] = card_number
            row["phone"] = phone
            row["expire"] = expire
            print('\n\n keldi \n\n')
            row["balance"] = clean_balance(row["balance"])

    
        except FormatError as e:
            print(f"Skipping row due to format error: {e}")
            kwargs.get("skip_row", lambda: None)()

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_class = CardResource
    list_display = ["card_number", "expire", "phone", "status", "balance"]
    list_filter = ["card_number", "expire", "phone", "status", "balance"]
    search_fields = ['card_number', 'phone']


