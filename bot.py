import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler,
    filters, 
    ContextTypes
)
from config import BOT_TOKEN
from states import NAME, CITY, MODEL, PHONE, CONSENT
from handlers_new import (
    start,
    language_selected,
    change_language,
    start_application,
    get_name,
    get_city,
    get_model,
    get_phone,
    get_consent,
    cancel,
    contacts,
    restart_bot
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^(📝 Подать заявку на покупку техники|📝 Uskunani sotib olish uchun ariza topshiring)$"), 
                start_application
            )
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_model)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
            CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_consent)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(❌ Отмена|❌ Bekor qilish)$"), cancel),
            CommandHandler("cancel", cancel)
        ],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.Regex("^(🇷🇺 Русский|🇺🇿 O'zbekcha)$"), 
        language_selected
    ))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(
        filters.Regex("^(📞 Узнать контакты|📞 Kontaktlarni toping)$"), 
        contacts
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^(🌐 Сменить язык|🌐 Tilni o'zgartirish)$"), 
        change_language
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^(🔄 Старт|🔄 Boshlash)$"), 
        restart_bot
    ))

    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()