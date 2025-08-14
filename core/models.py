from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
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


class Transfer(models.Model):
    
    class State(models.TextChoices):
        CREATED = 'created', 'Created'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        
        
    ext_id = models.CharField(max_length=50, unique=True)
    sender_card_number = models.CharField(max_length=16)
    receiver_card_number = models.CharField(max_length=16)
    sender_card_expiry = models.CharField(max_length=5)
    sender_phone = models.CharField(max_length=12, blank=True, null=True)
    receiver_phone = models.CharField(max_length=12, blank=True, null=True)
    sending_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.IntegerField(choices=((643, 'RUB'), (840, 'USD')))
    receiving_amount = models.DecimalField(max_digits=15, decimal_places=2)
    state = models.CharField(max_length=20, choices=[], default=State.CREATED)
    try_count = models.IntegerField(default=0)
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def clean(self):
        if not Card.objects.filter(card_number=self.sender_card_number, expiry=self.sender_card_expiry, status='active').exists():
            raise ValidationError("Sender card is not active or does not exist")
        if not Card.objects.filter(card_number=self.receiver_card_number).exists():
            raise ValidationError("Receiver card does not exist")
        if self.sending_amount <= 0:
            raise ValidationError("Amount must be positive")
        if self.currency not in [643, 840]:
            raise ValidationError("Currency not allowed except RUB(643), USD(840)")

    def __str__(self):
        return f"{self.ext_id}: {self.state}"
    
    
class Error(models.Model):
    code = models.IntegerField(unique=True)
    en = models.CharField(max_length=255)
    ru = models.CharField(max_length=255)
    uz = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code}: {self.en}"