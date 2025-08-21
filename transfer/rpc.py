# transfer/rpc.py
from decimal import Decimal
import json
from jsonrpcserver import method, Success, Error as JsonRpcError
from django.core.cache import cache
from jsonrpcserver import method
from core.models import Card, Transfer, Error
from utils.helper import format_card, format_expire, generate_otp, send_telegram_message, get_transfer_by_ext_id
from django.db.models import Q

from utils.log_decorator import log_request_response



@method
@log_request_response
def transfer_create(ext_id, sender_card_number, sender_card_expiry, receiver_card_number, sending_amount, currency):
    try:
        print("\n\n[TRANSFER CREATE] Keldi\n\n")

        if Transfer.objects.filter(ext_id=ext_id).exists():
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=str(error.en))

        sender_card_number = format_card(sender_card_number)
        receiver_card_number = format_card(receiver_card_number)
        sender_card_expiry = format_expire(sender_card_expiry)

        card = Card.objects.filter(status='active', card_number=sender_card_number).first()
        if not card:
            error = Error.objects.get(code=32705)
            return JsonRpcError(code=error.code, message=str(error.en))

        if Decimal(card.balance) < Decimal(sending_amount):
            error = Error.objects.get(code=32702)
            return JsonRpcError(code=error.code, message=str(error.en))

        if not Card.objects.filter(card_number=receiver_card_number).exists():
            return JsonRpcError(code=32705, message="Receiver card does not exist")

        if currency not in [643, 840]:
            error = Error.objects.get(code=32707)
            return JsonRpcError(code=error.code, message=str(error.en))

        if Decimal(sending_amount) > Decimal(1_000_000):
            error = Error.objects.get(code=32708)
            return JsonRpcError(code=error.code, message=str(error.en))
        if Decimal(sending_amount) < Decimal(100):
            error = Error.objects.get(code=32709)
            return JsonRpcError(code=error.code, message=str(error.en))

        otp = generate_otp()
        send_telegram_message(card.phone, f"Your OTP is {otp}")

        transfer = Transfer.objects.create(
            ext_id=ext_id,
            sender_card_number=sender_card_number,
            sender_card_expiry=sender_card_expiry,
            receiver_card_number=receiver_card_number,
            sender_phone=card.phone,
            sending_amount=sending_amount,
            currency=currency,
            receiving_amount=sending_amount,
            otp=otp,
        )

        return Success({
            "ext_id": ext_id,
            "state": transfer.state,  
            "otp_sent": True
        })

    except Exception as e:
        print(f"[TRANSFER CREATE EXCEPTION] {e}")
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=str(error.en))

@method
@log_request_response
def transfer_confirm(ext_id, otp):
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=str(error.en))

        if transfer.state != Transfer.State.CREATED:
            return JsonRpcError(code=32706, message="Transfer is not in created state")

        if transfer.otp != otp:
            transfer.try_count += 1
            transfer.save()
            if transfer.try_count >= 3:
                error = Error.objects.get(code=32711)
                return JsonRpcError(code=error.code, message=str(error.en))
            error = Error.objects.get(code=32712)
            return JsonRpcError(
                code=error.code,
                message=f"Incorrect OTP. Attempts left: {3 - transfer.try_count}"
            )

        card = Card.objects.filter(
            card_number=transfer.sender_card_number,
        ).first()   
        print("\n\n\n",card, "\n\n\n")
        if not card:
            error = Error.objects.get(code=32705)
            return JsonRpcError(code=error.code, message=str(error.en))

        # Подтверждаем трансфер
        transfer.state = Transfer.State.CONFIRMED
        transfer.save()

        return Success({
            "ext_id": ext_id,
            "state": transfer.state.value
        })

    except Exception as e:
        print(f"[TRANSFER CONFIRM EXCEPTION] {e}")
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=str(error.en))


@method
@log_request_response
def transfer_cancel(ext_id):
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            error = Error.objects.get(code=32701)
            return JsonRpcError(code=error.code, message=str(error.en))

        if transfer.state != Transfer.State.CREATED:
            return JsonRpcError(code=32706, message="Transfer is not in created state")

        transfer.state = Transfer.State.CANCELLED
        transfer.save()

        return Success({
            "ext_id": ext_id,
            "state": transfer.state
        })

    except Exception as e:
        print(f"[TRANSFER CANCEL EXCEPTION] {e}")
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=str(error.en))

@method
@log_request_response
def transfer_state(ext_id):
    try:
        cache_key = f"transfer_state:{ext_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"\n\ncach key {cache_key}\n\n")
            return cached_result
        print(f'\n\ncache key {cache_key} \n\n')
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            error = Error.objects.get(code=32701)
            result = JsonRpcError(code=error.code, message=str(error.en))
            cache.set(cache_key, result, timeout=30) 
            return result

        result = Success({
            "ext_id": ext_id,
            "state": transfer.state
        })

        cache.set(cache_key, result, timeout=30)
        return result

    except Exception as e:
        print(f"[TRANSFER STATE EXCEPTION] {e}")
        error = Error.objects.get(code=32706)
        result = JsonRpcError(code=error.code, message=str(error.en))
        cache.set(cache_key, result, timeout=30)
        return result
    
    
@method
@log_request_response
def transfer_history(card_number, start_date=None, end_date=None, status=None):
    try:
        card_number = format_card(card_number)
        cache_key = f"transfer_history:{card_number}:{start_date}:{end_date}:{status}"
        cached_result = cache.get(cache_key)
        if cached_result:
            print(cache_key)
            return Success(json.loads(cached_result))

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
                "ext_id": t.ext_id,
                "sending_amount": float(t.sending_amount),
                "state": t.state, 
                "created_at": t.created_at.isoformat()
            }
            for t in transfers
        ]
        cache.set(cache_key, json.dumps(result), timeout=30)
        return Success(result)

    except Exception as e:
        print(f"[TRANSFER HISTORY EXCEPTION] {e}")
        error = Error.objects.get(code=32706)
        return JsonRpcError(code=error.code, message=str(error.en))
