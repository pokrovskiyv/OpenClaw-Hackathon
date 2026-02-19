#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Пути к файлам
WORKSPACE = Path("/root/.openclaw/workspace")
CUSTOMERS_DIR = WORKSPACE / "customers"

def normalize_phone(phone):
    """Привести номер телефона к единому формату"""
    # Убираем все нецифровые символы кроме +
    normalized = re.sub(r'[^\d+]', '', phone.strip())
    return normalized

def find_customer_by_telegram(telegram_id):
    """Найти клиента по telegram_id"""
    if not CUSTOMERS_DIR.exists():
        return None
    
    for customer_file in CUSTOMERS_DIR.glob("customer_*.json"):
        try:
            with open(customer_file, 'r') as f:
                customer = json.load(f)
                if customer.get('telegram_id') == telegram_id:
                    return customer
        except:
            continue
    return None

def find_customer_by_phone(phone):
    """Найти клиента по номеру телефона"""
    normalized = normalize_phone(phone)
    index_file = CUSTOMERS_DIR / "index.json"
    
    if not index_file.exists():
        return None
    
    with open(index_file, 'r') as f:
        index = json.load(f)
    
    # Пробуем найти в индексе
    for stored_phone, customer_id in index.items():
        if normalize_phone(stored_phone) == normalized:
            customer_file = CUSTOMERS_DIR / f"{customer_id}.json"
            if customer_file.exists():
                with open(customer_file, 'r') as f:
                    return json.load(f)
    return None

def save_customer_profile(profile):
    """Сохранить профиль клиента"""
    customer_file = CUSTOMERS_DIR / f"{profile['customer_id']}.json"
    
    with open(customer_file, 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Обновить индекс
    index_file = CUSTOMERS_DIR / "index.json"
    index = {}
    if index_file.exists():
        with open(index_file, 'r') as f:
            index = json.load(f)
    
    if profile.get('phone'):
        normalized = normalize_phone(profile['phone'])
        index[normalized] = profile['customer_id']
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    return profile

def create_basic_profile(telegram_id, phone=None):
    """Создать базовый профиль клиента"""
    import uuid
    from datetime import datetime
    
    customer_id = f"customer_{uuid.uuid4().hex[:8]}"
    
    profile = {
        "customer_id": customer_id,
        "telegram_id": telegram_id,
        "phone": normalize_phone(phone) if phone else "",
        "name": "",
        "email": "",
        "address": {
            "street": "",
            "city": "",
            "state": "",
            "zip": ""
        },
        "driver_license": {
            "number": "",
            "state": "",
            "expiration_date": ""
        },
        "policy": {
            "policy_id": "",
            "status": "",
            "effective_date": "",
            "expiration_date": "",
            "vehicle": {
                "vin": "",
                "make": "",
                "model": "",
                "year": "",
                "license_plate": ""
            }
        },
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    save_customer_profile(profile)
    return profile

def handle_incoming_message(telegram_id):
    """
    Обработать входящее сообщение от клиента
    
    Возвращает:
    - (True, "OK") - если всё в порядке
    - (False, "сообщение об ошибке") - если нужно ввести номер телефона
    """
    # Найти клиента по telegram_id
    customer = find_customer_by_telegram(telegram_id)
    
    if not customer:
        # Клиента нет, создадим базовый профиль
        create_basic_profile(telegram_id)
        return False, "Привет! Пожалуйста, введите ваш номер телефона"
    
    if not customer.get('phone'):
        # Номер телефона не указан
        return False, "Пожалуйста, введите ваш номер телефона"
    
    # Клиент есть и номер телефона указан
    return True, "OK"

def update_customer_phone(telegram_id, phone):
    """Обновить номер телефона клиента"""
    customer = find_customer_by_telegram(telegram_id)
    if not customer:
        return False, "Клиент не найден"
    
    customer['phone'] = normalize_phone(phone)
    save_customer_profile(customer)
    return True, f"Номер телефона сохранён: {phone}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 customer_handler.py <telegram_id> [phone]")
        sys.exit(1)
    
    telegram_id = sys.argv[1]
    phone = sys.argv[2] if len(sys.argv) > 2 else None
    
    if phone:
        result, message = update_customer_phone(telegram_id, phone)
    else:
        result, message = handle_incoming_message(telegram_id)
    
    print(f"Result: {result}")
    print(f"Message: {message}")
