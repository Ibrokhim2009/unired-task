from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.models import Card

# Register your models here.

class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        import_id_fields = ['card_number']
        fields = ['card_number', 'expire', 'phone', 'status', 'balance']
        export_order = ['card_number', 'expire', 'phone', 'status', 'balance']







@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_class = CardResource
    list_display = ["card_number", "expire", "phone", "status", "balance"]
    list_filter = ["card_number", "expire", "phone", "status", "balance"]
    search_fields = ['card_number', 'phone']


