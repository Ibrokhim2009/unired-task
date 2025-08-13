# Unired Task Project Documentation

## 1. Overview

API on Django (JSON-RPC 2.0) for managing bank cards and transfers. Base URL: `http://localhost:8000/rpc` (locally). All requests are POST, JSON format.

## 2. Requirements

### Security

- **CORS**: Access restricted to `http://localhost:5173`.
- **Rate Limit**: `transfer.confirm` — 5 requests/min/IP.

### Data Formats (For admin panel; validation not required for imports)

- `card_number`: 16 digits, no spaces (`8600123456789012`).
- `phone`: `+998xxxxxxxxx` or empty.
- `expiry`: `MM/YY` (`12/26`).
- `currency`: 643 (RUB), 840 (USD).
- `amount`: Number (min. 1, max. depends on currency).

## 3. API Methods

### `transfer.create`

**Description**: Creates a transfer, sends OTP.  
**Request**:

```json
{"id": 1, "method": "transfer.create", "params": {"ext_id": "tr-uuid-12345", "sender_card_number": "8600123456789012", "sender_card_expiry": "12/26", "receiver_card_number": "8600567812345678", "sending_amount": 15000, "currency": 643}}
```

**Response**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "created", "otp_sent": true}}
```

### `transfer.confirm`

**Description**: Confirms a transfer using OTP (max. 3 attempts).  
**Request**:

```json
{"id": 1, "method": "transfer.confirm", "params": {"ext_id": "tr-uuid-12345", "otp": "123456"}}
```

**Response**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "confirmed"}}
```

### `transfer.cancel`

**Description**: Cancels a transfer (in `created` state).  
**Request**:

```json
{"id": 1, "method": "transfer.cancel", "params": {"ext_id": "tr-uuid-12345"}}
```

**Response**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "cancelled"}}
```

### `transfer.state`

**Description**: Checks the status of a transfer.  
**Request**:

```json
{"id": 1, "method": "transfer.state", "params": {"ext_id": "tr-uuid-12345"}}
```

**Response**:

```json
{"id": 1, "result": {"ext_id": "tr-uuid-12345", "state": "confirmed"}}
```

### `transfer.history`

**Description**: Retrieves transfer history with filters.  
**Request**:

```json
{"id": 1, "method": "transfer.history", "params": {"card_number": "8600123456789012", "start_date": "2025-04-01", "end_date": "2025-04-21", "status": "confirmed"}}
```

**Response**:

```json
{"id": 1, "result": [{"ext_id": "tr-uuid-12345", "sending_amount": 15000, "state": "confirmed", "created_at": "2025-04-10T08:30:00"}]}
```

## 4. Errors

Format: `{"id": null, "error": {"code": 32700, "message": "Ext id must be unique"}}`.  
Example errors:

- 32700: `Ext id must be unique`
- 32702: `Insufficient funds`
- 32712: `Invalid OTP, 2 attempts remaining`