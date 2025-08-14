import datetime
from decimal import Decimal, InvalidOperation
import re

class FormatError(Exception):
    pass

def card_mask(card_number):
    card = str(card_number).replace(' ','')
    return f'{card[:4]} **** **** {card[-4:]}'

def phone_mask(phone):
    digits = "".join(i for i in str(phone) if i.isdigit())
    if len(digits) == 12:
        return f"+{digits[:3]} ({digits[3:5]}) *** ** {digits[-2:]}"
    if len(digits) == 9:
        return f"+998 ({digits[:2]}) *** ** {digits[-2:]}"
    return digits


def format_card(raw_card):
    if isinstance(raw_card, (float, int)):
        raw_card = int(raw_card)
    card_number = ''.join(ch for ch in str(raw_card) if ch.isdigit())
    if len(card_number) > 16:
        card_number = card_number[:16]

    if len(card_number) != 16:
        raise FormatError(f"Card number is incorrect: {raw_card}")

    return card_number


def format_phone(raw_phone):
    digits = "".join(ch for ch in str(raw_phone) if ch.isdigit())
    if digits.startswith('0'):
        digits = digits[1:]
        print('\n\n\n keldi =>>>>>>>>>> \n\n\n', len(digits))
        
    
    if len(digits) == 7:
        return f'+998 ** *** {digits[3:5]} {digits[-2:]}'
    if len(digits) == 9:
        return f"+998 ** *** {digits[5:7]} {digits[7:]}"
    elif len(digits) == 12 and digits.startswith("998"):
        return f"+{digits[:3]} *** {digits[5:8]} {digits[8:10]} {digits[10:]}"    
    return  



def format_expire(raw_expire):
    if isinstance(raw_expire,(int,float)):
        raw_expire = datetime.datetime.fromordinal(int(raw_expire) + 693594).strftime('%m/%y')
    elif isinstance(raw_expire, datetime.datetime):
        raw_expire = raw_expire.strftime('%m/%y')
    digits = re.findall(r"\d+", str(raw_expire))
    if len(digits) < 2:
        raise FormatError(f"Invalid date format: {raw_expire}")
    parts = [int(num) for num in digits]
    if parts[0] > 31:  
        year, month = parts[0], parts[1]
    else:
        month, year = parts[0], parts[1]
    if not (1 <= month <= 12):
        raise FormatError(f"Invalid month: {month}")
    return f"{month:02d}/{year % 100:02d}"

def prepare_message(card_number, balance, lang="UZ"):
    masked_card = card_mask(card_number)
    balance_str = f"{balance:,.2f}"
    messages = {
        "UZ": f"Sizning kartangiz {masked_card} aktiv va foydalanishga {balance_str} UZS mavjud!",
        "RU": f"Ваша карта {masked_card} активна, на ней доступно {balance_str} UZS!",
        "EN": f"Your card {masked_card} is active with {balance_str} UZS available!"
    }
    return messages.get(lang.upper(), messages["UZ"])

def send_message(phone, message, chat_id=123456):
    print(f"Sending message to {phone}: {message}")
    return f"Simulating message send: '{message}' to chat ID: {chat_id}"




def clean_balance(raw_balance):
    try:
        if raw_balance is None:
            return Decimal("0.00")
        balance_str = str(raw_balance).strip()
        balance_str = balance_str.replace(",", "")
        if not balance_str:
            return Decimal("0.00")
        return Decimal(balance_str)

    except (InvalidOperation, TypeError, ValueError):
        raise FormatError(f"Неверный баланс: {raw_balance}")
    
    