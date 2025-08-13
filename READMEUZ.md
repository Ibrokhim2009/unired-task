# Unired Task loyihasi uchun hujjat

## 1. Umumiy ma'lumot

Bank kartalari va pul o‘tkazmalarini boshqarish uchun Django asosidagi API (JSON-RPC 2.0). Asosiy URL: `http://localhost:8000/rpc` (lokal muhitda). Barcha so‘rovlar — POST, JSON formatida.

## 2. Talablar

### Xavfsizlik

- **CORS**: Faqat `http://localhost:5173` uchun ruxsat beriladi.
- **Cheklov**: `transfer.confirm` — IP manzili bo‘yicha daqiqasiga 5 ta so‘rov.

### Ma'lumot formatlari (Admin paneli uchun, import uchun bu tekshiruvlar shart emas)

- `card_number`: 16 raqam, bo‘shliqsiz (`8600123456789012`).
- `phone`: `+998xxxxxxxxx` yoki bo‘sh.
- `expiry`: `MM/YY` (`12/26`).
- `currency`: 643 (RUB), 840 (USD).
- `amount`: Raqam (min. 1, maks. valyutaga bog‘liq).

## 3. API metodlari

### `transfer.create`

**Tavsif**: Pul o‘tkazmasini yaratadi, OTP yuboradi.\
**So‘rov**:

```json
{"id": 1, "method": "transfer.create", "params": {"ext_id": "tr-uuid-12345", "sender_card_number": "8600123456789012", "sender_card_expiry": "12/26", "receiver_card_number": "8600567812345678", "sending_amount": 15000, "currency": 643}}
```

**Javob**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "created", "otp_sent": true}}
```

### `transfer.confirm`

**Tavsif**: OTP orqali pul o‘tkazmasini tasdiqlaydi (maks. 3 urinish).\
**So‘rov**:

```json
{"id": 1, "method": "transfer.confirm", "params": {"ext_id": "tr-uuid-12345", "otp": "123456"}}
```

**Javob**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "confirmed"}}
```

### `transfer.cancel`

**Tavsif**: Pul o‘tkazmasini bekor qiladi (`created` holatida).\
**So‘rov**:

```json
{"id": 1, "method": "transfer.cancel", "params": {"ext_id": "tr-uuid-12345"}}
```

**Javob**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "cancelled"}}
```

### `transfer.state`

**Tavsif**: Pul o‘tkazmasi holatini tekshiradi.\
**So‘rov**:

```json
{"id": 1, "method": "transfer.state", "params": {"ext_id": "tr-uuid-12345"}}
```

**Javob**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "confirmed"}}
```

### `transfer.history`

**Tavsif**: Filtrlar bilan pul o‘tkazmalari tarixini ko‘rsatadi.\
**So‘rov**:

```json
{"id": 1, "method": "transfer.history", "params": {"card_number": "8600123456789012", "start_date": "2025-04-01", "end_date": "2025-04-21", "status": "confirmed"}}
```

**Javob**:

```json
{"id": 1, "result": [{"ext_id": "tr-uuid-12345", "sending_amount": 15000, "state": "confirmed", "created_at": "2025-04-10T08:30:00"}]}
```

## 4. Xatolar

Format: `{"id": null, "error": {"code": 32700, "message": "Ext id noyob bo'lishi kerak"}}`.\
Xato misollari:

- 32700: `Ext id noyob bo'lishi kerak`
- 32702: `Hisobda mablag‘ yetarli emas`
- 32712: `Noto‘g‘ri OTP, yana 2 urinish qoldi`