import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colored import cprint
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Состояния для ConversationHandler
CHOOSING, ACCOUNT_TYPE, CHANNEL_TYPE, BOT_TYPE, CHAT_TYPE, ADDING_EMAILS = range(6)

# Глобальные переменные для хранения данных пользователя
user_data = {}
senders = {}

def start(update: Update, context: CallbackContext) -> int:
    """Начало взаимодействия с пользователем, показывает главное меню."""
    keyboard = [
        [InlineKeyboardButton("СНОС АККАУНТОВ", callback_data='1')],
        [InlineKeyboardButton("СНОС КАНАЛОВ", callback_data='2')],
        [InlineKeyboardButton("СНОС БОТОВ", callback_data='3')],
        [InlineKeyboardButton("СНОС ЧАТОВ", callback_data='4')],
        [InlineKeyboardButton("Добавить почты", callback_data='add_emails')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Выберите тип жалобы:",
        reply_markup=reply_markup
    )
    
    return CHOOSING

def start_over(update: Update, context: CallbackContext) -> int:
    """Повторное отображение главного меню."""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("СНОС АККАУНТОВ", callback_data='1')],
        [InlineKeyboardButton("СНОС КАНАЛОВ", callback_data='2')],
        [InlineKeyboardButton("СНОС БОТОВ", callback_data='3')],
        [InlineKeyboardButton("СНОС ЧАТОВ", callback_data='4')],
        [InlineKeyboardButton("Добавить почты", callback_data='add_emails')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Выберите тип жалобы:",
        reply_markup=reply_markup
    )
    
    return CHOOSING

def account_type_choice(update: Update, context: CallbackContext) -> int:
    """Выбор типа жалобы для аккаунтов."""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("1. ЗА СПАМ, РЕКЛАМУ", callback_data='acc_1')],
        [InlineKeyboardButton("2. ЗА ДОКСИНГ", callback_data='acc_2')],
        [InlineKeyboardButton("3. ЗА ТРОЛЛИНГ(ОСК)", callback_data='acc_3')],
        [InlineKeyboardButton("4. ПРОДАЖА/РЕКЛАМА НАРКОТЫ", callback_data='acc_4')],
        [InlineKeyboardButton("5. КУРАТОРСТВО В НАРКОШОПЕ", callback_data='acc_5')],
        [InlineKeyboardButton("6. ПРОДАЖА ЦП", callback_data='acc_6')],
        [InlineKeyboardButton("7. ВЫМОГАНИЕ ИНТИМНЫХ ФОТО", callback_data='acc_7')],
        [InlineKeyboardButton("8. УГНЕТАНИЕ НАЦИИ", callback_data='acc_8')],
        [InlineKeyboardButton("9. УГНЕТАНИЕ РЕЛИГИИ", callback_data='acc_9')],
        [InlineKeyboardButton("10. РАСПРОСТРАНЯЕТ РАСЧЛЕНЕНКУ", callback_data='acc_10')],
        [InlineKeyboardButton("11. РАСПРОСТРАНЯЕТ ЖИВОДЕРКУ", callback_data='acc_11')],
        [InlineKeyboardButton("12. РАСПРОСТРАНЯЕТ ПОРНУХУ", callback_data='acc_12')],
        [InlineKeyboardButton("13. СУТЕНЕР(ШЛЮХ ПРОДАЕТ)", callback_data='acc_13')],
        [InlineKeyboardButton("14. ПРИЗЫВ К САМОВЫПИЛУ", callback_data='acc_14')],
        [InlineKeyboardButton("15. ПРИЗЫВ К ТЕРРОРУ", callback_data='acc_15')],
        [InlineKeyboardButton("16. УГРОЗЫ СВАТА И ТП", callback_data='acc_16')],
        [InlineKeyboardButton("17. УГРОЗЫ РАСПРАВЫ", callback_data='acc_17')],
        [InlineKeyboardButton("18. СНОС СЕССИЙ", callback_data='acc_18')],
        [InlineKeyboardButton("19. С ВИРТ НОМЕРОМ", callback_data='acc_19')],
        [InlineKeyboardButton("20. С ПРЕМКОЙ", callback_data='acc_20')],
        [InlineKeyboardButton("21. ПРОСТО СНОС (НЕ ЭФФЕКТИВЕН)", callback_data='acc_21')],
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Выберите тип жалобы для аккаунта:",
        reply_markup=reply_markup
    )
    
    return ACCOUNT_TYPE

def channel_type_choice(update: Update, context: CallbackContext) -> int:
    """Выбор типа жалобы для каналов."""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("1. С ЛИЧНЫМИ ДАННЫМИ", callback_data='ch_1')],
        [InlineKeyboardButton("2. С ЖИВОДЕРСТВОМ", callback_data='ch_2')],
        [InlineKeyboardButton("3. С ДЕТСКИМ ПОРНО", callback_data='ch_3')],
        [InlineKeyboardButton("4. ДЛЯ КАНАЛОВ ТИПА ПРАЙСОВ", callback_data='ch_4')],
        [InlineKeyboardButton("5. С РАСЧЛЕНЕНКОЙ", callback_data='ch_5')],
        [InlineKeyboardButton("6. РУЛЕТКИ (КАЗИК)", callback_data='ch_6')],
        [InlineKeyboardButton("7. НАРКО-ШОП", callback_data='ch_7')],
        [InlineKeyboardButton("8. ПРИЗЫВ К ТЕРРОРУ", callback_data='ch_8')],
        [InlineKeyboardButton("9. ПРИЗЫВ К САМОВЫПИЛУ", callback_data='ch_9')],
        [InlineKeyboardButton("10. РАЗЖИГАНИЕ НЕНАВИСТИ", callback_data='ch_10')],
        [InlineKeyboardButton("11. ПРОПАГАНДА НАСИЛИЯ", callback_data='ch_11')],
        [InlineKeyboardButton("12. ПРОДАЖА ДЕТСКИХ ИНТИМОК", callback_data='ch_12')],
        [InlineKeyboardButton("13. УГНЕТЕНИЕ НАЦИИ", callback_data='ch_13')],
        [InlineKeyboardButton("14. УГНЕТЕНИЕ РЕЛИГИИ", callback_data='ch_14')],
        [InlineKeyboardButton("15. С ПОРНУХОЙ", callback_data='ch_15')],
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Выберите тип жалобы для канала:",
        reply_markup=reply_markup
    )
    
    return CHANNEL_TYPE

def bot_type_choice(update: Update, context: CallbackContext) -> int:
    """Выбор типа жалобы для ботов."""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("1. ГЛАЗ БОГА", callback_data='bot_1')],
        [InlineKeyboardButton("2. ТИПА СИНЕГО КИТА", callback_data='bot_2')],
        [InlineKeyboardButton("3. ПРОДАЖА ЦП", callback_data='bot_3')],
        [InlineKeyboardButton("4. МОШЕННИЧЕСКИЕ СХЕМЫ", callback_data='bot_4')],
        [InlineKeyboardButton("5. СПАМ, РЕКЛАМА", callback_data='bot_5')],
        [InlineKeyboardButton("6. ШАНТАЖ", callback_data='bot_6')],
        [InlineKeyboardButton("7. ИЗВРАЩЕНИЯ(СНАФФ,ЦП И ТП)", callback_data='bot_7')],
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Выберите тип жалобы для бота:",
        reply_markup=reply_markup
    )
    
    return BOT_TYPE

def chat_type_choice(update: Update, context: CallbackContext) -> int:
    """Выбор типа жалобы для чатов."""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("1. ПРОСТО СНОС(НЕ ЭФФЕКТИВЕН)", callback_data='chat_1')],
        [InlineKeyboardButton("2. СПАМ/РЕКЛАМА", callback_data='chat_2')],
        [InlineKeyboardButton("3. ЗА АВУ ИЛИ НАЗВАНИЕ", callback_data='chat_3')],
        [InlineKeyboardButton("4. ПРОПАГАНДА НАСИЛИЯ И ТП", callback_data='chat_4')],
        [InlineKeyboardButton("5. НАКРУТКА", callback_data='chat_5')],
        [InlineKeyboardButton("6. ОСКИ В ЧАТЕ", callback_data='chat_6')],
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text="Выберите тип жалобы для чата:",
        reply_markup=reply_markup
    )
    
    return CHAT_TYPE

def ask_for_username(update: Update, context: CallbackContext) -> int:
    """Запрос username у пользователя."""
    query = update.callback_query
    query.answer()
    
    # Сохраняем тип жалобы в user_data
    complaint_type = query.data
    user_data[update.effective_user.id] = {'complaint_type': complaint_type}
    
    query.edit_message_text(text="Введите username пользователя:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_username)

def ask_for_channel_link(update: Update, context: CallbackContext) -> int:
    """Запрос ссылки на канал у пользователя."""
    query = update.callback_query
    query.answer()
    
    # Сохраняем тип жалобы в user_data
    complaint_type = query.data
    user_data[update.effective_user.id] = {'complaint_type': complaint_type}
    
    query.edit_message_text(text="Введите ссылку на канал:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_channel_link)

def ask_for_bot_username(update: Update, context: CallbackContext) -> int:
    """Запрос username бота у пользователя."""
    query = update.callback_query
    query.answer()
    
    # Сохраняем тип жалобы в user_data
    complaint_type = query.data
    user_data[update.effective_user.id] = {'complaint_type': complaint_type}
    
    query.edit_message_text(text="Введите username бота:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_bot_username)

def ask_for_chat_link(update: Update, context: CallbackContext) -> int:
    """Запрос ссылки на чат у пользователя."""
    query = update.callback_query
    query.answer()
    
    # Сохраняем тип жалобы в user_data
    complaint_type = query.data
    user_data[update.effective_user.id] = {'complaint_type': complaint_type}
    
    query.edit_message_text(text="Введите ссылку на чат:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_chat_link)

def process_username(update: Update, context: CallbackContext) -> int:
    """Обработка username и запрос ID."""
    user_id = update.effective_user.id
    user_data[user_id]['username'] = update.message.text
    
    update.message.reply_text("Введите TG ID пользователя:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_id)

def process_id(update: Update, context: CallbackContext) -> int:
    """Обработка ID и запрос дополнительной информации в зависимости от типа жалобы."""
    user_id = update.effective_user.id
    user_data[user_id]['id'] = update.message.text
    
    complaint_type = user_data[user_id]['complaint_type']
    
    if complaint_type in ['acc_18', 'acc_19', 'acc_20', 'acc_21']:
        # Для этих типов жалоб не нужны дополнительные данные
        return send_complaints(update, context)
    else:
        update.message.reply_text("Введите ссылку на чат:")
        return MessageHandler(Filters.text & ~Filters.command, process_chat_link_for_account)

def process_chat_link_for_account(update: Update, context: CallbackContext) -> int:
    """Обработка ссылки на чат и запрос ссылки на нарушение."""
    user_id = update.effective_user.id
    user_data[user_id]['chat_link'] = update.message.text
    
    update.message.reply_text("Введите ссылку на нарушение:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_violation_link)

def process_violation_link(update: Update, context: CallbackContext) -> int:
    """Обработка ссылки на нарушение и начало отправки жалоб."""
    user_id = update.effective_user.id
    user_data[user_id]['violation_link'] = update.message.text
    
    return send_complaints(update, context)

def process_channel_link(update: Update, context: CallbackContext) -> int:
    """Обработка ссылки на канал и запрос ссылки на нарушение."""
    user_id = update.effective_user.id
    user_data[user_id]['channel_link'] = update.message.text
    
    update.message.reply_text("Введите ссылку на нарушение:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_channel_violation_link)

def process_channel_violation_link(update: Update, context: CallbackContext) -> int:
    """Обработка ссылки на нарушение в канале и начало отправки жалоб."""
    user_id = update.effective_user.id
    user_data[user_id]['channel_violation'] = update.message.text
    
    return send_complaints(update, context)

def process_bot_username(update: Update, context: CallbackContext) -> int:
    """Обработка username бота и начало отправки жалоб."""
    user_id = update.effective_user.id
    user_data[user_id]['bot_username'] = update.message.text
    
    return send_complaints(update, context)

def process_chat_link(update: Update, context: CallbackContext) -> int:
    """Обработка ссылки на чат и запрос ID чата."""
    user_id = update.effective_user.id
    user_data[user_id]['chat_link'] = update.message.text
    
    complaint_type = user_data[user_id]['complaint_type']
    
    if complaint_type == 'chat_6':
        update.message.reply_text("Введите ссылку на нарушение:")
        return MessageHandler(Filters.text & ~Filters.command, process_chat_violation_link)
    else:
        update.message.reply_text("Введите TG ID чата:")
        return MessageHandler(Filters.text & ~Filters.command, process_chat_id)

def process_chat_id(update: Update, context: CallbackContext) -> int:
    """Обработка ID чата и начало отправки жалоб."""
    user_id = update.effective_user.id
    user_data[user_id]['chat_id'] = update.message.text
    
    return send_complaints(update, context)

def process_chat_violation_link(update: Update, context: CallbackContext) -> int:
    """Обработка ссылки на нарушение в чате и запрос ID чата."""
    user_id = update.effective_user.id
    user_data[user_id]['violation_link'] = update.message.text
    
    update.message.reply_text("Введите TG ID чата:")
    
    return MessageHandler(Filters.text & ~Filters.command, process_chat_id)

def send_email(receiver, sender_email, sender_password, subject, body):
    """Функция отправки email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if 'gmail.com' in sender_email:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
        elif 'rambler.ru' in sender_email:
            smtp_server = 'smtp.rambler.ru'
            smtp_port = 587
        elif 'hotmail.com' in sender_email:
            smtp_server = 'smtp.office365.com'
            smtp_port = 587
        elif 'mail.ru' in sender_email:
            smtp_server = 'smtp.mail.ru'
            smtp_port = 587
        else:
            raise ValueError("Unsupported email provider")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
        return False

def send_complaints(update: Update, context: CallbackContext) -> int:
    """Отправка жалоб на основе собранных данных."""
    user_id = update.effective_user.id
    data = user_data.get(user_id, {})
    complaint_type = data.get('complaint_type', '')
    
    # Определяем текст жалобы в зависимости от типа
    if complaint_type.startswith('acc_'):
        # Жалобы на аккаунты
        comp_texts = {
            "acc_1": f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя который отправляет много ненужных сообщений - СПАМ. Его юзернейм - {data['username']}, его айди - {data['id']}, ссылка на чат - {data['chat_link']}, ссылка на нарушения - {data['violation_link']}. Пожалуйста примите меры по отношению к данному пользователю.",
            "acc_2": f"Здравствуйте, уважаемая поддержка, на вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. его юзернейм - {data['username']}, его айди - {data['id']}, ссылка на чат - {data['chat_link']}, ссылка на нарушение/нарушения - {data['violation_link']}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта.",
            # ... остальные тексты жалоб для аккаунтов
            "acc_18": f"Здравствуйте, уважаемая поддержка. Я случайно перешел по фишинговой ссылке и утерял доступ к своему аккаунту. Его юзернейм - {data['username']}, его айди - {data['id']}. Пожалуйста удалите аккаунт или обнулите сессии",
            "acc_21": f"Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел пользователя с подозрительной активностью на аккаунте. Его юзернейм - {data['username']}, его айди - {data['id']}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки аккаунта."
        }
        subject = 'Жалоба на аккаунт телеграм'
        body = comp_texts.get(complaint_type, '')
        
    elif complaint_type.startswith('ch_'):
        # Жалобы на каналы
        comp_texts = {
            "ch_1": f"Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел канал, который распространяет личные данные невинных людей. Ссылка на канал - {data['channel_link']}, ссылки на нарушения - {data['channel_violation']}. Пожалуйста заблокируйте данный канал.",
            # ... остальные тексты жалоб для каналов
        }
        subject = 'Жалоба на телеграм канал'
        body = comp_texts.get(complaint_type, '')
        
    elif complaint_type.startswith('bot_'):
        # Жалобы на ботов
        comp_texts = {
            "bot_1": f"Здравствуйте, уважаемая поддержка телеграм. На вашей платформе я нашел бота, который осуществляет поиск по личным данным ваших пользователей. Ссылка на бота - {data['bot_username']}. Пожалуйста разберитесь и заблокируйте данного бота.",
            # ... остальные тексты жалоб для ботов
        }
        subject = 'Жалоба на бота телеграм'
        body = comp_texts.get(complaint_type, '')
        
    elif complaint_type.startswith('chat_'):
        # Жалобы на чаты
        comp_texts = {
            "chat_1": f"Здравствуйте, уважаемая поддержка телеграмма. На вашей платформе я нашел группу с подозрительной активностью. Ссылка на группу - {data['chat_link']}, Айди группы - {data['chat_id']}. Пожалуйста примите меры в сторону данной группы и заблокируйте ее.",
            "chat_6": f"Здравствуйте, уважаемая поддержка телеграмма. Я нашел группу с которой оскорбляют людей и используют ненормативную лексику в их сторону. Ссылка на группу - {data['chat_link']}, Айди группы - {data['chat_id']}, Ссылка на нарушение - {data['violation_link']}. Пожалуйста примите меры в сторону этой группы и заблокируйте ее как можно скорее"
        }
        subject = 'Жалоба на группу телеграм'
        body = comp_texts.get(complaint_type, '')
    
    receivers = ['sms@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org', 'sticker@telegram.org', 'support@telegram.org']
    
    # Отправка жалоб с каждой почты
    sent_count = 0
    for receiver in receivers:
        for sender_email, sender_password in senders.items():
            success = send_email(receiver, sender_email, sender_password, subject, body)
            status = "✅ Успешно" if success else "❌ Ошибка"
            update.message.reply_text(f"Отправлено на {receiver} от {sender_email} - {status}")
            sent_count += 1
            time.sleep(5)  # Задержка между отправками
    
    update.message.reply_text(f"Всего отправлено {sent_count} жалоб.")
    
    return start_over(update, context)

def add_emails_start(update: Update, context: CallbackContext) -> int:
    """Начало процесса добавления почт."""
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        text="Отправьте файл с почтами в формате:\n"
             "email1:password1\n"
             "email2:password2\n"
             "...\n\n"
             "Или введите почты вручную в том же формате:"
    )
    
    return ADDING_EMAILS

def add_emails(update: Update, context: CallbackContext) -> int:
    """Обработка добавления почт."""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли документ
    if update.message.document:
        file = context.bot.get_file(update.message.document.file_id)
        file.download('emails.txt')
        
        with open('emails.txt', 'r') as f:
            email_lines = f.read().splitlines()
    else:
        email_lines = update.message.text.split('\n')
    
    added_count = 0
    for line in email_lines:
        if ':' in line:
            email, password = line.split(':', 1)
            senders[email.strip()] = password.strip()
            added_count += 1
    
    update.message.reply_text(f"Добавлено {added_count} почт. Всего почт: {len(senders)}")
    
    return start_over(update, context)

def cancel(update: Update, context: CallbackContext) -> int:
    """Завершение диалога."""
    update.message.reply_text('Диалог завершен. Нажмите /start для начала нового.')
    return ConversationHandler.END

def main() -> None:
    """Запуск бота."""
    # Создаем Updater и передаем ему токен бота
    updater = Updater(TOKEN)
    
    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher
    
    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(account_type_choice, pattern='^1$'),
                CallbackQueryHandler(channel_type_choice, pattern='^2$'),
                CallbackQueryHandler(bot_type_choice, pattern='^3$'),
                CallbackQueryHandler(chat_type_choice, pattern='^4$'),
                CallbackQueryHandler(add_emails_start, pattern='^add_emails$'),
            ],
            ACCOUNT_TYPE: [
                CallbackQueryHandler(ask_for_username, pattern='^acc_'),
                CallbackQueryHandler(start_over, pattern='^back$'),
            ],
            CHANNEL_TYPE: [
                CallbackQueryHandler(ask_for_channel_link, pattern='^ch_'),
                CallbackQueryHandler(start_over, pattern='^back$'),
            ],
            BOT_TYPE: [
                CallbackQueryHandler(ask_for_bot_username, pattern='^bot_'),
                CallbackQueryHandler(start_over, pattern='^back$'),
            ],
            CHAT_TYPE: [
                CallbackQueryHandler(ask_for_chat_link, pattern='^chat_'),
                CallbackQueryHandler(start_over, pattern='^back$'),
            ],
            ADDING_EMAILS: [
                MessageHandler(Filters.text | Filters.document, add_emails),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Регистрируем обработчик
    dispatcher.add_handler(conv_handler)
    
    # Запускаем бота
    updater.start_polling()
    
    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
