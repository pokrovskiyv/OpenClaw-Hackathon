#!/usr/bin/env python3
import json
from customer_store import normalize_phone, find_customer_by_telegram, find_customer_by_phone, save_customer_profile
import re
from pathlib import Path

# Пути к файлам
WORKSPACE = Path("/root/.openclaw/workspace")
CUSTOMERS_DIR = WORKSPACE / "customers"

def check_phone_number(telegram_id):
    """
    Проверить, есть ли у клиента номер телефона
    
    Возвращает:
    - (True, "OK") - если номер есть
    - (False, "сообщение об ошибке") - если номера нет
    """
    customer = find_customer_by_telegram(telegram_id)
    
    if not customer:
        # Создаём базовый профиль
        return False, "Please enter your phone number"
    
    if not customer.get('phone'):
        return False, "Please enter your phone number"
    
    return True, "OK"

def save_phone_number(telegram_id, phone):
    """Сохранить номер телефона клиента"""
    customer = find_customer_by_telegram(telegram_id)
    if not customer:
        return False, "Customer not found"
    
    customer = dict(customer, phone=normalize_phone(phone))
    save_customer_profile(customer)
    save_customer_profile(customer)
    return True, f"Phone number saved: {phone}"

def is_admin_command(message):
    """Проверить, является ли сообщение командой админа"""
    commands = [
        r'add\s+client',
        r'add\s+customer',
        r'create\s+client',
        r'create\s+customer',
        r'update\s+client',
        r'update\s+customer',
        r'добавь\s+клиента',
        r'добавь\s+пользователя',
        r'обнови\s+клиента',
        r'обнови\s+пользователя'
    ]
    
    message_lower = message.lower()
    for pattern in commands:
        if re.search(pattern, message_lower):
            return True
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 command_handler.py <command> [args...]")
        print("Commands:")
        print("  check_phone <telegram_id>")
        print("  save_phone <telegram_id> <phone>")
        print("  is_admin <message>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check_phone":
        telegram_id = sys.argv[2]
        result, message = check_phone_number(telegram_id)
        print(f"Result: {result}")
        print(f"Message: {message}")
    
    elif command == "save_phone":
        telegram_id = sys.argv[2]
        phone = sys.argv[3]
        result, message = save_phone_number(telegram_id, phone)
        print(f"Result: {result}")
        print(f"Message: {message}")
    
    elif command == "is_admin":
        message = sys.argv[2]
        result = is_admin_command(message)
        print(f"Result: {result}")
