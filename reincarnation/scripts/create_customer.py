#!/usr/bin/env python3
import json
from customer_store import normalize_phone, save_customer_profile
import re
import uuid
import subprocess
from datetime import datetime, timezone, timezone
from pathlib import Path

# Пути к файлам
WORKSPACE = Path("/root/.openclaw/workspace")
CUSTOMERS_DIR = WORKSPACE / "customers"
INDEX_FILE = CUSTOMERS_DIR / "index.json"

def ensure_customers_dir():
    """Создать директорию для клиентов"""
    CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not INDEX_FILE.exists():
        with open(INDEX_FILE, 'w') as f:
            json.dump({}, f)

def load_index():
    """Загрузить индекс"""
    with open(INDEX_FILE, 'r') as f:
        return try:
            json.load(f)
        except (json.JSONDecodeError, OSError, KeyError, ValueError) as e:
            print(f"JSON loading error: {e}", file=sys.stderr)
            return None

def save_index(index):
    """Сохранить индекс"""
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

def parse_ocr_text(text):
    """Распарсить распознанный текст"""
    data = {}
    
    # Персональная информация
    first_name_match = re.search(r'First Name:\s*([A-Z]+)', text)
    if first_name_match:
        data['first_name'] = first_name_match.group(1).strip()
    
    last_name_match = re.search(r'Last Name:\s*([A-Z]+)', text)
    if last_name_match:
        data['last_name'] = last_name_match.group(1).strip()
    
    phone_match = re.search(r'Phone Number:\s*\((\d{3})\)\s*(\d{3})-(\d{4})', text)
    if phone_match:
        data['phone'] = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"
    
    email_match = re.search(r'Email Address:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    if email_match:
        data['email'] = email_match.group(1).strip()
    
    # Адрес
    street_match = re.search(r'Street Address:\s*([^\n]+)', text)
    if street_match:
        data['street'] = street_match.group(1).strip()
    
    city_match = re.search(r'City:\s*([^\n]+)', text)
    if city_match:
        city = city_match.group(1).strip()
        city = re.sub(r'\n+', ' ', city)
        city = re.sub(r'\s+', ' ', city)
        data['city'] = city
    
    state_match = re.search(r'State:\s*([A-Z]{2})\s*Zip Code:', text)
    if state_match:
        data['state'] = state_match.group(1).strip()
    
    zip_match = re.search(r'Zip Code:\s*(\d{5})', text)
    if zip_match:
        data['zip'] = zip_match.group(1).strip()
    
    # Водительские права
    license_match = re.search(r'License Number:\s*([A-Z0-9-]+)', text)
    if license_match:
        data['license_number'] = license_match.group(1).strip()
    
    license_state_match = re.search(r'State of Issue:\s*([A-Z]{2})\s*Expiration Date:', text)
    if license_state_match:
        data['license_state'] = license_state_match.group(1).strip()
    
    license_expiry_match = re.search(r'Expiration Date:\s*(\d{2}/\d{2}/\d{4})', text)
    if license_expiry_match:
        data['license_expiry'] = license_expiry_match.group(1)
    
    # Полис
    policy_match = re.search(r'Policy Number\.?\s*([A-Z0-9-]+)', text)
    if policy_match:
        data['policy_id'] = policy_match.group(1).strip()
    
    status_match = re.search(r'Status:\s*([A-Z]+)', text)
    if status_match:
        data['policy_status'] = status_match.group(1).strip()
    
    policy_start_match = re.search(r'Effective Date \(Start\):\s*(\d{2}/\d{2}/\d{4})', text)
    if policy_start_match:
        data['policy_start'] = policy_start_match.group(1)
    
    policy_end_match = re.search(r'Expiration Date \(End\):\s*(\d{2}/\d{2}/\d{4})', text)
    if policy_end_match:
        data['policy_end'] = policy_end_match.group(1)
    
    # Автомобиль
    vin_match = re.search(r'VIN \(Vehicle ID Number\):\s*([A-Z0-9]+)', text)
    if vin_match:
        data['vin'] = vin_match.group(1).strip()
    
    make_match = re.search(r'Make \(Brand\):\s*([A-Z]+)', text)
    if make_match:
        data['make'] = make_match.group(1).strip()
    
    model_match = re.search(r'Model;\s*([A-Z\s0-9]+)', text)
    if model_match:
        model = model_match.group(1).strip()
        model = ' '.join(model.split())
        data['model'] = model
    
    year_match = re.search(r'Year:\s*(\d{4})', text)
    if year_match:
        data['year'] = int(year_match.group(1))
    
    plate_match = re.search(r'License Plate:\s*([A-Z0-9-]+)', text)
    if plate_match:
        data['license_plate'] = plate_match.group(1).strip()
    
    return data

def create_customer_profile(data, telegram_id=None):
    """Создать профиль клиента в формате JSON"""
    customer_id = f"customer_{uuid.uuid4().hex[:8]}"
    
    profile = {
        "customer_id": customer_id,
        "telegram_id": telegram_id,
        "name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
        "phone": data.get('phone', ''),
        "email": data.get('email', ''),
        "address": {
            "street": data.get('street', ''),
            "city": data.get('city', ''),
            "state": data.get('state', ''),
            "zip": data.get('zip', '')
        },
        "driver_license": {
            "number": data.get('license_number', ''),
            "state": data.get('license_state', ''),
            "expiration_date": data.get('license_expiry', '')
        },
        "policy": {
            "policy_id": data.get('policy_id', ''),
            "status": data.get('policy_status', ''),
            "effective_date": data.get('policy_start', ''),
            "expiration_date": data.get('policy_end', ''),
            "vehicle": {
                "vin": data.get('vin', ''),
                "make": data.get('make', ''),
                "model": data.get('model', ''),
                "year": data.get('year', ''),
                "license_plate": data.get('license_plate', '')
            }
        },
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    return profile

def save_customer(profile):
    """Сохранить профиль клиента"""
    customer_file = CUSTOMERS_DIR / f"{profile['customer_id']}.json"
    
    with open(customer_file, 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Обновить индекс - добавляем телефон (если есть) с нормализацией
    index = load_index()
    if profile.get('phone'):
        normalized = normalize_phone(profile['phone'])
        if normalized:
            index[normalized] = profile['customer_id']
    save_index(index)
    
    return customer_file

def find_customer_by_phone(phone):
    """Найти клиента по номеру телефона"""
    normalized = normalize_phone(phone)
    if not normalized:
        return None
    
    index = load_index()
    if normalized in index:
        customer_id = index[normalized]
        customer_file = CUSTOMERS_DIR / f"{customer_id}.json"
        if customer_file.exists():
            try:
                with open(customer_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError, KeyError, ValueError) as e:
                print(f"JSON loading error: {e}", file=sys.stderr)
                return None
    return None

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
        except (json.JSONDecodeError, OSError, KeyError, ValueError) as e:
            print(f"JSON loading error for {customer_file.name}: {e}", file=sys.stderr)
            continue
    return None

def update_customer(customer_id, new_data):
    """Обновить профиль клиента"""
    customer_file = CUSTOMERS_DIR / f"{customer_id}.json"
    
    with open(customer_file, 'r') as f:
        profile = try:
            json.load(f)
        except (json.JSONDecodeError, OSError, KeyError, ValueError) as e:
            print(f"JSON loading error: {e}", file=sys.stderr)
            return None
    
    # Обновляем поля
    for key, value in new_data.items():
        if key == 'telegram_id' and value:
            profile['telegram_id'] = value
        elif key == 'name' and value:
            profile['name'] = value
        elif key == 'phone' and value:
            profile['phone'] = value
        elif key == 'email' and value:
            profile['email'] = value
        elif key == 'address' and value:
            for addr_key, addr_val in value.items():
                if addr_val:
                    profile['address'][addr_key] = addr_val
        elif key == 'driver_license' and value:
            for dl_key, dl_val in value.items():
                if dl_val:
                    profile['driver_license'][dl_key] = dl_val
        elif key == 'policy' and value:
            if 'vehicle' in value:
                for veh_key, veh_val in value['vehicle'].items():
                    if veh_val:
                        profile['policy']['vehicle'][veh_key] = veh_val
            for pol_key, pol_val in value.items():
                if pol_key != 'vehicle' and pol_val:
                    profile['policy'][pol_key] = pol_val
    
    profile['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    with open(customer_file, 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Обновить индекс если номер телефона изменился
    if new_data.get('phone'):
        index = load_index()
        index[new_data['phone']] = customer_id
        save_index(index)
    
    return profile

def process_image(image_path, telegram_id=None):
    """Обработать изображение"""
    output_file = f"/tmp/ocr_temp_{datetime.now(timezone.utc).timestamp()}"
    subprocess.run([
        'tesseract', str(image_path), output_file, '-l', 'eng'
    ], check=True, timeout=60)
    
    with open(f"{output_file}.txt", 'r') as f:
        text = f.read()
    
    data = parse_ocr_text(text)
    profile = create_customer_profile(data, telegram_id=telegram_id)
    customer_file = save_customer(profile)
    
    return profile, customer_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 create_customer.py <image_path> [telegram_id]")
        sys.exit(1)
    
    ensure_customers_dir()
    
    image_path = sys.argv[1]
    telegram_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    profile, customer_file = process_image(image_path, telegram_id=telegram_id)
    
    print(f"✓ Клиент создан: {profile['customer_id']}")
    print(f"✓ Имя: {profile['name']}")
    print(f"✓ Телефон: {profile['phone']}")
    print(f"✓ Telegram ID: {profile['telegram_id']}")
    print(f"✓ Файл: {customer_file}")
