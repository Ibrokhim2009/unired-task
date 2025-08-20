from decimal import Decimal
from jsonrpcserver import method, Error as JsonRpcError, Success
from core.models import Card, Transfer, Error
from utils.helper import *
from django.utils import timezone
from django.db.models import Q





# transfer/rpc.py
from jsonrpcserver import method

@method
def transfer_create(ext_id, sender_card_number, sender_card_expiry, receiver_card_number, sending_amount, currency):
    print("\n\n", "keldi" ,"\n\n")
    
    try:
        if Transfer.objects.filter(ext_id=ext_id).exists():
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=error.en)

        sender_card_number = format_card(sender_card_number)
        receiver_card_number = format_card(receiver_card_number)
        sender_card_expiry = format_expire(sender_card_expiry)

        card = Card.objects.filter(status='active').first()
        if not card:
            error = Error.objects.get(code=32705)
            return JsonRpcError(code=error.code, message=error.en)

        if Decimal(card.balance) < Decimal(sending_amount):
            error = Error.objects.get(code=32702)
            return JsonRpcError(code=error.code, message=error.en)



        if not Card.objects.filter(card_number=receiver_card_number).exists():
            error = Error.objects.get(code=32705)
            return JsonRpcError(code=32705, message="Receiver card does not exist")

        if currency not in [643, 840]:
            error = Error.objects.get(code=32707)
            return JsonRpcError(code=error.code, message=error.en)

        if Decimal(sending_amount) > Decimal(1_000_000):
            error = Error.objects.get(code=32708)
            return JsonRpcError(code=error.code, message=error.en)
        if Decimal(sending_amount) < Decimal(100):
            error = Error.objects.get(code=32709)
            return JsonRpcError(code=error.code, message=error.en)

        otp = generate_otp()
        send_telegram_message(card.phone, f"Your OTP is {otp}")

        print("shu yergacha keldi>>>>>")
        transfer = Transfer.objects.create(
            ext_id=ext_id,
            sender_card_number=sender_card_number,
            receiver_card_number=receiver_card_number,
            sender_card_expiry=sender_card_expiry,
            sender_phone=card.phone,
            sending_amount=sending_amount,
            currency=currency,
            receiving_amount=sending_amount,
            otp=otp,
        )

        print("\n\nbu yerda")
        return Success({
            "ext_id": ext_id,
            "state": transfer.state.value,
            "otp_sent": True
        })

    except Exception as e:
        print(f"\n\n\n\n\n{e}\n\n\n\n\n")
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=error.en)
    

@method
def transfer_confirm(ext_id, otp):
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=error.en)

        if transfer.state != Transfer.State.CREATED:
            return JsonRpcError(code=32706, message="Transfer is not in created state")

        if transfer.otp != otp:
            transfer.try_count += 1
            transfer.save()
            if transfer.try_count >= 3:
                error = Error.objects.get(code=32711)
                return JsonRpcError(code=error.code, message=error.en)
            error = Error.objects.get(code=32712)
            return JsonRpcError(
                code=error.code,
                message=f"Incorrect OTP. Attempts left: {3 - transfer.try_count}"
            )

        transfer.state = Transfer.State.CONFIRMED
        transfer.save() 

        return Success({
            "ext_id": ext_id,
            "state": transfer.state
        })

    except Exception as e:
        print(e)
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=error.en)

@method
def transfer_cancel(ext_id):
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=error.en)

        if transfer.state != Transfer.State.CREATED:
            return JsonRpcError(code=32706, message="Transfer is not in created state")

        transfer.state = Transfer.State.CANCELLED
        transfer.save()

        return Success({
            "ext_id": ext_id,
            "state": transfer.state
        })

    except Exception as e:
        print(e)
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=error.en)

@method
def transfer_state(ext_id):
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=error.en)

        return Success({
            "ext_id": ext_id,
            "state": transfer.state
        })

    except Exception as e:
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=error.en)

@method
def transfer_history(card_number, start_date=None, end_date=None, status=None):
    try:
        card_number = format_card(card_number)
        transfers = Transfer.objects.filter(
            Q(sender_card_number=card_number) | Q(receiver_card_number=card_number)
        )

        if start_date:
            transfers = transfers.filter(created_at__gte=start_date)
        if end_date:
            transfers = transfers.filter(created_at__lte=end_date)
        if status:
            transfers = transfers.filter(state=status)

        result = [
            {
                "ext_id": transfer.ext_id,
                "sending_amount": float(transfer.sending_amount),
                "state": transfer.state,
                "created_at": transfer.created_at.isoformat()
            }
            for transfer in transfers
        ]

        return Success(result)

    except Exception as e:
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=error.en)
    
    
    
