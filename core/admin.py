from django.contrib import admin

from core.models import Card

# Register your models here.





@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ["card_number", "expire", "phone", "status", "balance"]
    list_filter = ["card_number", "expire", "phone", "status", "balance"]


