import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Включите журналирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройка базы данных
Base = declarative_base()
engine = create_engine('sqlite:///faq.db')
Session = sessionmaker(bind=engine)
session = Session()


# Определение модели данных
class FAQ(Base):
    __tablename__ = 'faq'
    id = Column(Integer, primary_key=True)
    question = Column(String, unique=True)
    answer = Column(Text)


Base.metadata.create_all(engine)

# ID администратора
ADMIN_ID = 'admin_id'


# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\! Напиши мне свой вопрос, и я постараюсь ответить\.',
        reply_markup=ForceReply(selective=True),
    )


# Обработка сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    faq_entry = session.query(FAQ).filter(FAQ.question.ilike(f"%{user_message}%")).first()

    if faq_entry:
        await update.message.reply_text(faq_entry.answer)
    else:
        await update.message.reply_text("Извините, я не нашел ответа на ваш вопрос. Я передам его администратору.")
        await context.bot.send_message(chat_id=ADMIN_ID,
                                       text=f"Новый вопрос от {update.message.from_user.username}: {user_message}")


# Команда /addfaq для добавления вопросов и ответов (только для админа)
async def add_faq(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != int(ADMIN_ID):
        await update.message.reply_text("Эта команда доступна только администратору.")
        return

    try:
        question, answer = update.message.text.split('?', 1)
        question = question.strip() + '?'
        answer = answer.strip()

        new_faq = FAQ(question=question, answer=answer)
        session.add(new_faq)
        session.commit()

        await update.message.reply_text("FAQ успешно добавлен.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении FAQ: {e}")


def main() -> None:
    # Вставьте здесь ваш токен бота
    application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addfaq", add_faq))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()
