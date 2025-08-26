import json
import os
import random
from datetime import datetime

APPLICATIONS_FILE = "applications.json"
APPLICATION_COUNTER_FILE = "counter.json"

def get_next_application_number():
    counter = 1000
    if os.path.exists(APPLICATION_COUNTER_FILE):
        with open(APPLICATION_COUNTER_FILE, 'r') as f:
            try:
                data = json.load(f)
                counter = data.get('counter', 1000)
            except:
                counter = 1000
    
    counter += 1
    
    with open(APPLICATION_COUNTER_FILE, 'w') as f:
        json.dump({'counter': counter}, f)
    
    return f"#{counter}"

def save_application(user_data):
    application = {
        "id": get_next_application_number(),
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "user_id": user_data.get('user_id'),
        "username": user_data.get('username'),
        "name": user_data.get('name'),
        "city": user_data.get('city'),
        "model": user_data.get('model'),
        "phone": user_data.get('phone')
    }
    
    applications = []
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
            try:
                applications = json.load(f)
            except json.JSONDecodeError:
                applications = []
    
    applications.append(application)
    
    with open(APPLICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(applications, f, ensure_ascii=False, indent=2)
    
    return application['id']

def get_all_applications():
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []