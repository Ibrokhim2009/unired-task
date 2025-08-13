from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.






class Card(models.Model):
    STATUS_CHOICES=[
        ("active","Active"),
        ("inactive", "Inactive"),
        ("expired", "Expired")
    ]
    
    card_number = models.CharField(_("Card number"), max_length=16, unique=True)
    expire = models.CharField(_("Card expire date"), max_length=5)
    phone = models.CharField(_("Phone number"), max_length=20, blank=True, null=True)
    status = models.CharField(_("Transfer status"), choices=STATUS_CHOICES)
    balance = models.DecimalField(_("Card balance"), max_digits=15, decimal_places=2)
    
    
    def __str__(self):
        return f"{self.card_number}"
    
    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"


