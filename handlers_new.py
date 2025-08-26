import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import NAME, CITY, MODEL, PHONE, CONSENT
from keyboards import get_phone_keyboard, get_cancel_keyboard, get_main_keyboard, get_language_keyboard, get_consent_keyboard
from database import save_application
from translations import get_text
from user_data import save_user_language, get_user_language
from config import BOT_TOKEN

ADMIN_IDS = []
CHANNEL_ID = "-1002849406135"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_lang = get_user_language(user.id)
    
    # Проверяем, был ли уже выбран язык (проверяем наличие файла с языками пользователя)
    import os
    from user_data import USER_LANG_FILE
    
    user_has_language = False
    if os.path.exists(USER_LANG_FILE):
        try:
            import json
            with open(USER_LANG_FILE, 'r') as f:
                languages = json.load(f)
                user_has_language = str(user.id) in languages
        except:
            user_has_language = False
    
    if not user_has_language:  # Если язык не выбран, предлагаем выбрать
        await update.message.reply_text(
            get_text('ru', 'language_choice'),
            reply_markup=get_language_keyboard()
        )
    else:
        await update.message.reply_html(
            get_text(user_lang, 'welcome'),
            reply_markup=get_main_keyboard(user_lang)
        )

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🇷🇺 Русский":
        lang = 'ru'
    elif text == "🇺🇿 O'zbekcha":
        lang = 'uz'
    else:
        return
    
    save_user_language(user_id, lang)
    
    await update.message.reply_text(
        get_text(lang, 'welcome'),
        reply_markup=get_main_keyboard(lang),
        parse_mode='HTML'
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        get_text('ru', 'language_choice'),
        reply_markup=get_language_keyboard()
    )

async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_lang = get_user_language(user_id)
    
    context.user_data.clear()
    context.user_data['user_id'] = user_id
    context.user_data['username'] = update.effective_user.username
    context.user_data['lang'] = user_lang
    
    await update.message.reply_text(
        get_text(user_lang, 'start_application'),
        reply_markup=get_cancel_keyboard(user_lang)
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_lang = context.user_data.get('lang', 'ru')
    name = update.message.text.strip()
    
    if name == get_text(user_lang, 'cancel'):
        return await cancel(update, context)
    
    if len(name) < 3:
        await update.message.reply_text(
            get_text(user_lang, 'name_too_short')
        )
        return NAME
    
    context.user_data['name'] = name
    await update.message.reply_text(
        get_text(user_lang, 'ask_city').format(name),
        reply_markup=get_cancel_keyboard(user_lang)
    )
    return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_lang = context.user_data.get('lang', 'ru')
    city = update.message.text.strip()
    
    if city == get_text(user_lang, 'cancel'):
        return await cancel(update, context)
    
    if len(city) < 2:
        await update.message.reply_text(
            get_text(user_lang, 'city_too_short')
        )
        return CITY
    
    context.user_data['city'] = city
    await update.message.reply_text(
        get_text(user_lang, 'ask_model'),
        reply_markup=get_cancel_keyboard(user_lang)
    )
    return MODEL

async def get_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_lang = context.user_data.get('lang', 'ru')
    model = update.message.text.strip()
    
    if model == get_text(user_lang, 'cancel'):
        return await cancel(update, context)
    
    if len(model) < 2:
        await update.message.reply_text(
            get_text(user_lang, 'model_too_short')
        )
        return MODEL
    
    context.user_data['model'] = model
    await update.message.reply_text(
        get_text(user_lang, 'ask_phone'),
        reply_markup=get_phone_keyboard(user_lang)
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_lang = context.user_data.get('lang', 'ru')
    
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
    else:
        text = update.message.text.strip()
        
        if text == get_text(user_lang, 'cancel'):
            return await cancel(update, context)
        
        # Удаляем все пробелы, скобки, тире
        digits_only = re.sub(r'[^\d]', '', text)
        
        # Проверяем, что введено ровно 9 цифр
        if len(digits_only) != 9:
            await update.message.reply_text(
                get_text(user_lang, 'phone_invalid'),
                reply_markup=get_phone_keyboard(user_lang)
            )
            return PHONE
        
        # Форматируем номер
        phone = f"+998 {digits_only[:2]} {digits_only[2:5]} {digits_only[5:7]} {digits_only[7:9]}"
    
    context.user_data['phone'] = phone
    
    await update.message.reply_text(
        get_text(user_lang, 'ask_consent'),
        reply_markup=get_consent_keyboard(user_lang)
    )
    return CONSENT

async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_lang = context.user_data.get('lang', 'ru')
    text = update.message.text.strip()
    
    if text == get_text(user_lang, 'cancel'):
        return await cancel(update, context)
    
    if text == get_text(user_lang, 'consent_agree'):
        # Пользователь дал согласие, сохраняем заявку
        phone = context.user_data['phone']
        application_id = save_application(context.user_data)
        
        await update.message.reply_text(
            get_text(user_lang, 'application_success').format(
                application_id,
                context.user_data['name'],
                context.user_data['city'],
                context.user_data['model'],
                phone
            ),
            reply_markup=get_main_keyboard(user_lang),
            parse_mode='HTML'
        )
        
        # Отправка в канал
        if CHANNEL_ID:
            try:
                username = context.user_data.get('username', 'нет')
                username_text = f"@{username}" if username != 'нет' else '—'
                current_time = datetime.now().strftime("%d.%m.%Y в %H:%M")
                
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"🎯 <b>НОВАЯ ЗАЯВКА {application_id}</b>\n"
                         f"━━━━━━━━━━━━━━━━━━━━\n\n"
                         f"👤 <b>Клиент:</b> {context.user_data['name']}\n"
                         f"📍 <b>Город:</b> {context.user_data['city']}\n"
                         f"🚜 <b>Интересует:</b> {context.user_data['model']}\n"
                         f"📞 <b>Телефон:</b> <code>{phone}</code>\n"
                         f"💬 <b>Telegram:</b> {username_text}\n\n"
                         f"━━━━━━━━━━━━━━━━━━━━\n"
                         f"🕐 <i>{current_time}</i>",
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Ошибка отправки в канал: {e}")
        
        # Отправка админам
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🔔 Новая заявка!\n\n"
                         f"📋 Номер: {application_id}\n"
                         f"👤 Имя: {context.user_data['name']}\n"
                         f"🏙 Город: {context.user_data['city']}\n"
                         f"🚜 Модель: {context.user_data['model']}\n"
                         f"📱 Телефон: {phone}\n"
                         f"👤 Username: @{context.user_data.get('username', 'нет')}"
                )
            except:
                pass
        
        context.user_data.clear()
        return ConversationHandler.END
    else:
        # Если пользователь выбрал что-то другое, повторяем запрос согласия
        await update.message.reply_text(
            get_text(user_lang, 'ask_consent'),
            reply_markup=get_consent_keyboard(user_lang)
        )
        return CONSENT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_lang = context.user_data.get('lang', get_user_language(update.effective_user.id))
    await update.message.reply_text(
        get_text(user_lang, 'application_cancelled'),
        reply_markup=get_main_keyboard(user_lang)
    )
    context.user_data.clear()
    return ConversationHandler.END

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_lang = get_user_language(update.effective_user.id)
    await update.message.reply_text(
        get_text(user_lang, 'contacts'),
        parse_mode='Markdown'
    )

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        get_text('ru', 'language_choice'),
        reply_markup=get_language_keyboard()
    )