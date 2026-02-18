Хранение профилей клиентов:

Поскольку базы данных нет — используем JSON файлы:

```
~/.openclaw/workspace/customers/
├── index.json              # Индекс: phone → customer_id
├── customer_001.json       # Профиль клиента 1
├── customer_002.json       # Профиль клиента 2
└── ...Структура профиля клиента:
```

```json
{
  "customer_id": "customer_001",
  "name": "John Smith",
  "phone": "+15551234567",
  "email": "john.smith@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "zip": "90001"
  },
  "driver_license": {
    "number": "D1234567",
    "state": "CA",
    "expiration_date": "2025-06-15"
  },
  "policy": {
    "policy_id": "POL-2024-001",
    "status": "active",
    "effective_date": "2024-01-01",
    "expiration_date": "2024-12-31",
    "coverages": {
      "liability": {...},
      "collision": {...},
      "comprehensive": {...}
    },
    "vehicle": {
      "vin": "1HGCM82633A123456",
      "make": "Honda",
      "model": "Civic",
      "year": 2019,
      "license_plate": "ABC1234"
    }
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

Индекс для быстрого поиска:

```json
{
  "+15551234567": "customer_001",
  "+15559876543": "customer_002"
}
```

**Регистрация в чате:**

• Пользователь пишет в чате
• Я прошу: номер телефона + данные для профиля
• Создаю профиль с номером телефона
• Теперь он может звонить

```
Ты: зарегистрируй меня
Я: Хорошо. Нужны: имя, номер телефона, email, адрес, водительские права, данные полиса и авто.
Ты: [предоставляет]
Я: Создаю профиль... Готово! Теперь можешь звонить, я узнаю тебя по номеру.
```

**При звонке:**

• Получаю номер телефона от ClawdTalk (Caller ID)
• Ищу в customers/index.json
• Если найден → запускаю 6-агентный pipeline
• Если не найден → "Клиент не найден. Соединяю с оператором."
