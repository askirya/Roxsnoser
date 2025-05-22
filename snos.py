import logging
import asyncio
import smtplib
import ssl
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

RECEIVERS = [
    'sms@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org',
    'sticker@telegram.org', 'support@telegram.org'
]
user_email_dumps = {}  # {user_id: {email: password}}

class ReportStates(StatesGroup):
    selecting_category = State()
    entering_data = State()
    collecting_emails = State()

categories = {
    "1": "СПАМ / РЕКЛАМА",
    "2": "ДОКСИНГ / СЛИВ ДАННЫХ",
    "3": "ОСКОРБЛЕНИЯ / ТРОЛЛИНГ",
    "4": "НАРКОТИКИ",
    "5": "КУРАТОРСТВО",
    "6": "ДЕТСКОЕ ПОРНО",
    "7": "ВЫМОГАНИЕ ИНТИМА",
    "8": "УГНЕТЕНИЕ НАЦИИ",
    "9": "УГНЕТЕНИЕ РЕЛИГИИ",
    "10": "РАСЧЛЕНЕНКА",
    "11": "ЖИВОДЕРСТВО",
    "12": "ПОРНОГРАФИЯ",
    "13": "ПРОСТИТУЦИЯ",
    "14": "ПРИЗЫВ К СУИЦИДУ",
    "15": "ТЕРРОРИЗМ",
    "16": "УГРОЗЫ",
    "17": "ФИШИНГ / СНОС СЕССИЙ"
}
templates = {
    key: f"Здравствуйте, уважаемая поддержка. Нарушитель: {{username}}, ID: {{id}}, ссылка: {{link}}. Категория: {val}. Пожалуйста примите меры."
    for key, val in categories.items()
}

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📩 Добавить почты")],
        [KeyboardButton(text="📨 Начать жалобу")],
        [KeyboardButton(text="📬 Мои почты"), KeyboardButton(text="📤 Выгрузить рабочие почты")],
        [KeyboardButton(text="❌ Удалить все почты")]
    ], resize_keyboard=True)
    await message.answer("👋 Добро пожаловать! Я бот для рассылки жалоб в Telegram.\nВыберите действие:", reply_markup=kb)

def parse_emails_passwords(text: str):
    pattern = re.compile(
        r"""['"]?([\w\.-]+@[\w\.-]+\.\w+)['"]?\s*[:=]\s*['"]?([^'",\s]+)['"]?""",
        re.MULTILINE
    )
    return pattern.findall(text)

async def check_email_login(email: str, password: str) -> bool:
    try:
        if 'gmail.com' in email:
            smtp = 'smtp.gmail.com'
            port = 587
        elif 'mail.ru' in email or 'rambler.ru' in email:
            smtp = 'smtp.mail.ru'
            port = 587
        else:
            smtp = 'smtp.office365.com'
            port = 587

        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp, port, timeout=10)
        server.starttls(context=context)
        server.login(email, password)
        server.quit()
        return True
    except Exception as e:
        logging.warning(f"Ошибка проверки почты {email}: {e}")
        return False

@dp.message(F.text == "📩 Добавить почты")
async def request_emails(message: Message, state: FSMContext):
    await state.set_state(ReportStates.collecting_emails)
    await message.answer(
        "📧 Введите почты с паролями в любом формате:\n"
        "'email':'pass', \"email\":\"pass\", email:pass и т.д.\n"
        "⚠️ Для Mail.ru и Rambler.ru используйте ПАРОЛЬ ПРИЛОЖЕНИЯ!\n"
        "Как получить: https://help.mail.ru/mail/security/protection/external"
    )

@dp.message(ReportStates.collecting_emails)
async def save_emails(message: Message, state: FSMContext):
    text = message.text.strip()
    pairs = parse_emails_passwords(text)
    if not pairs:
        await message.answer("❌ Не удалось найти пары email:password. Попробуйте ещё раз.")
        return
    added = len(pairs)
    valid = 0
    for email, password in pairs:
        email = email.strip()
        password = password.strip()
        if await check_email_login(email, password):
            user_email_dumps.setdefault(message.from_user.id, {})[email] = password
            valid += 1
    await state.clear()
    await message.answer(f"✅ Добавлено {added} почт, из них рабочих: {valid}.")

@dp.message(F.text == "📬 Мои почты")
async def my_emails(message: Message):
    emails = user_email_dumps.get(message.from_user.id, {})
    if emails:
        email_list = '\n'.join(emails.keys())
        await message.answer(f"📥 У вас загружено {len(emails)} почт:\n<code>{email_list}</code>", parse_mode="HTML")
    else:
        await message.answer("📥 У вас нет загруженных почт.")

@dp.message(F.text == "📤 Выгрузить рабочие почты")
async def export_emails(message: Message):
    dump = user_email_dumps.get(message.from_user.id)
    if not dump:
        return await message.answer("❌ У вас нет загруженных почт.")
    text = '\n'.join(f"{k}:{v}" for k, v in dump.items())
    await message.answer(f"<b>📤 Ваша выгрузка:</b>\n<code>{text}</code>", parse_mode="HTML")

@dp.message(F.text == "❌ Удалить все почты")
async def delete_all_emails(message: Message):
    if message.from_user.id in user_email_dumps:
        user_email_dumps.pop(message.from_user.id)
        await message.answer("🗑 Все ваши почты удалены.")
    else:
        await message.answer("ℹ У вас нет загруженных почт.")

@dp.message(F.text == "📨 Начать жалобу")
async def begin_report(message: Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    for key, value in categories.items():
        kb.add(KeyboardButton(text=f"{key}. {value}"))
    kb.adjust(2)
    await message.answer("Выберите категорию жалобы:", reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(ReportStates.selecting_category)

@dp.message(ReportStates.selecting_category)
async def get_category(message: Message, state: FSMContext):
    code = message.text.split('.')[0]
    if code not in categories:
        return await message.answer("❌ Неверная категория. Повторите выбор.")
    await state.update_data(template_id=code)
    await state.set_state(ReportStates.entering_data)
    await message.answer("✏ Введите данные через ;\nФормат: USERNAME;ID;ССЫЛКА")

async def send_email(receiver: str, sender_email: str, sender_password: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if 'gmail.com' in sender_email:
            smtp = 'smtp.gmail.com'
            port = 587
        elif 'mail.ru' in sender_email or 'rambler.ru' in sender_email:
            smtp = 'smtp.mail.ru'
            port = 587
        else:
            smtp = 'smtp.office365.com'
            port = 587

        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp, port, timeout=10)
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

@dp.message(ReportStates.entering_data)
async def process_report_data(message: Message, state: FSMContext):
    if message.from_user.id not in user_email_dumps or not user_email_dumps[message.from_user.id]:
        return await message.answer("❌ Сначала добавьте почты через 📩 Добавить почты")
    try:
        username, user_id, link = [s.strip() for s in message.text.split(';')]
    except Exception:
        return await message.answer("❌ Формат неверный. Используйте USERNAME;ID;ССЫЛКА")
    data = await state.get_data()
    template = templates[data['template_id']]
    body = template.format(username=username, id=user_id, link=link)
    dump = user_email_dumps.get(message.from_user.id)
    success = 0
    fail = 0
    for sender_email, sender_password in dump.items():
        for receiver in RECEIVERS:
            result, error = await send_email(receiver, sender_email, sender_password, "Telegram Жалоба", body)
            if result:
                await message.answer(f"✅ {receiver} ← {sender_email}")
                success += 1
            else:
                await message.answer(f"❌ {receiver} ← {sender_email}. Ошибка: {error}")
                fail += 1
            await asyncio.sleep(1)
    await state.clear()
    await message.answer(f"📬 Готово. Успешно: {success}, Ошибок: {fail}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
