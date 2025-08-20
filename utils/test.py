

def format_card(raw_card):
    if isinstance(raw_card, (float, int)):
        raw_card = int(raw_card)
    card_number = ''.join(ch for ch in str(raw_card) if ch.isdigit())
    if len(card_number) > 16:
        card_number = card_number[:16]

    if len(card_number) != 16:
        raise (f"Card number is incorrect: {raw_card}")

    return card_number



def validate_card(card_number):
    digits = []
    for i in format_card(card_number):
        digits.append(int(i)) 
    checksum = 0
    is_even = False
    for digit in digits[::-1]:
        if is_even:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
        is_even = not is_even
    return checksum % 10 == 0
print(validate_card('5105 1051 0510 5100'))