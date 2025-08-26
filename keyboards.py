from telegram import ReplyKeyboardMarkup, KeyboardButton
from translations import get_text

def get_language_keyboard():
    keyboard = [
        ["🇺🇿 O'zbekcha"],
        ["🇷🇺 Русский"]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=True,
        input_field_placeholder="",
        selective=False
    )

def get_phone_keyboard(lang='ru'):
    keyboard = [
        [KeyboardButton(get_text(lang, 'send_contact'), request_contact=True)],
        [get_text(lang, 'cancel')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, selective=False)

def get_cancel_keyboard(lang='ru'):
    keyboard = [[get_text(lang, 'cancel')]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, selective=False)

def get_consent_keyboard(lang='ru'):
    keyboard = [
        [get_text(lang, 'consent_agree')],
        [get_text(lang, 'cancel')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, selective=False)

def get_main_keyboard(lang='ru'):
    keyboard = [
        [get_text(lang, 'main_menu_application')],
        [get_text(lang, 'main_menu_contacts')],
        [get_text(lang, 'main_menu_language'), get_text(lang, 'main_menu_start')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True, selective=False)