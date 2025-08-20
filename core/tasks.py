
from celery import shared_task
from core.models import Card, Transfer
from django.utils import timezone
import requests
from django.conf import settings


@shared_task
def send_report():
    total_cards = Card.objects.count()
    total_transfers = Transfer.objects.count()

    message = (
        f"Telegram Report - {timezone.now().strftime('%Y-%m-%d %H:%M')}:\n"
        f"Total Card Count: {total_cards}\n"
        f"Total Transfer Count: {total_transfers}"
    )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": settings.TELEGRAM_CHAT_ID, "text": message})

    # Добавим проверку успешности отправки
    if response.status_code != 200:
        print(f"Failed to send Telegram message: {response.text}")