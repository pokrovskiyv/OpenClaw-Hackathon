#!/usr/bin/env python3
"""Customer storage module - shared functions for customer management"""

import json
import re
from pathlib import Path

CUSTOMERS_DIR = Path.home() / ".openclaw" / "workspace" / "customers"

def normalize_phone(phone):
    """Нормализовать номер телефона: +381628568502 -> 381628568502"""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('380') and len(digits) == 12:
        return digits
    if digits.startswith('38') and len(digits) == 11:
        return '3' + digits
    if len(digits) == 10:
        return '380' + digits
    return digits

def find_customer_by_telegram(telegram_id):
    """Найти клиента по Telegram ID"""
    try:
        customer_file = CUSTOMERS_DIR / f"customer_{telegram_id}.json"
        if customer_file.exists():
            with open(customer_file, 'r') as f:
                return json.load(f)
        return None
    except (json.JSONDecodeError, OSError, KeyError) as e:
        print(f"Error finding customer by telegram: {e}", file=__import__('sys').stderr)
        return None

def find_customer_by_phone(phone):
    """Найти клиента по номеру телефона"""
    try:
        normalized = normalize_phone(phone)
        index_file = CUSTOMERS_DIR / "index.json"
        
        if not index_file.exists():
            return None
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        for stored_phone, customer_id in index.items():
            if normalize_phone(stored_phone) == normalized:
                customer_file = CUSTOMERS_DIR / f"customer_{customer_id}.json"
                if customer_file.exists():
                    with open(customer_file, 'r') as f:
                        return json.load(f)
        return None
    except (json.JSONDecodeError, OSError, KeyError, IOError) as e:
        print(f"Error finding customer by phone: {e}", file=__import__('sys').stderr)
        return None

def save_customer_profile(customer):
    """Сохранить профиль клиента"""
    try:
        CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)
        
        customer_id = customer.get('customer_id') or customer.get('telegram_id')
        if not customer_id:
            print("Error: No customer_id or telegram_id", file=__import__('sys').stderr)
            return False
        
        customer_file = CUSTOMERS_DIR / f"customer_{customer_id}.json"
        
        with open(customer_file, 'w') as f:
            json.dump(customer, f, indent=2)
        
        # Обновляем индекс
        index_file = CUSTOMERS_DIR / "index.json"
        index = {}
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index = json.load(f)
            except (json.JSONDecodeError, OSError):
                index = {}
        
        phone = customer.get('phone', '')
        if phone:
            normalized = normalize_phone(phone)
            index[normalized] = customer_id
            
            with open(index_file, 'w') as f:
                json.dump(index, f, indent=2)
        
        return True
    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"Error saving customer profile: {e}", file=__import__('sys').stderr)
        return False
