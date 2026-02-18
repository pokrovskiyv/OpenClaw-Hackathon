#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

# Пути
SKILL_DIR = Path("/root/.openclaw/workspace/skills/clawdtalk-client")
CONFIG_FILE = SKILL_DIR / "skill-config.json"

def load_config():
    """Загрузить конфиг"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def make_call(phone_number=None, greeting="", purpose=""):
    """Сделать звонок"""
    config = load_config()
    api_key = config.get('api_key')
    server = config.get('server', 'https://clawdtalk.com')
    
    # Собираем payload
    payload = {}
    
    if phone_number:
        payload['to'] = phone_number
        if greeting:
            payload['greeting'] = greeting
        if purpose:
            payload['context'] = {'purpose': purpose}
    else:
        if greeting:
            payload['greeting'] = greeting
    
    # Делаем запрос через curl
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'{server}/v1/calls',
        '-H', f'Authorization: Bearer {api_key}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout), result.returncode

if __name__ == "__main__":
    import sys
    
    phone = sys.argv[1] if len(sys.argv) > 1 else None
    greeting = sys.argv[2] if len(sys.argv) > 2 else ""
    purpose = sys.argv[3] if len(sys.argv) > 3 else ""
    
    result, code = make_call(phone, greeting, purpose)
    
    if code == 0:
        status = result.get('status', result.get('error', {}).get('code', 'unknown'))
        if status in ['initiating', 'ringing']:
            print(f"✓ Call initiated: {result.get('call_id', 'N/A')}")
        else:
            error = result.get('error', {}).get('message', 'Unknown error')
            print(f"✗ Error: {error}")
    else:
        print(f"✗ Request failed with code {code}")
