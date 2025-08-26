import json
import os

USER_LANG_FILE = "user_languages.json"

def save_user_language(user_id, lang):
    languages = {}
    if os.path.exists(USER_LANG_FILE):
        with open(USER_LANG_FILE, 'r') as f:
            try:
                languages = json.load(f)
            except:
                languages = {}
    
    languages[str(user_id)] = lang
    
    with open(USER_LANG_FILE, 'w') as f:
        json.dump(languages, f)

def get_user_language(user_id):
    if os.path.exists(USER_LANG_FILE):
        with open(USER_LANG_FILE, 'r') as f:
            try:
                languages = json.load(f)
                return languages.get(str(user_id), 'ru')
            except:
                return 'ru'
    return 'ru'