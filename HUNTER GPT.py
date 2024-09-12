import logging
import openai
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# إعدادات التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توكن البوت من @BotFather
TELEGRAM_TOKEN = '7237707856:AAEv54G0Cr-HJJngzFcGASeoCy9Nz0lKNZw'
# مفتاح API من OpenAI
OPENAI_API_KEY = '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'
# إعداد مفتاح API لـ OpenAI
openai.api_key = OPENAI_API_KEY

# دالة لتحويل الصوت إلى نص
def audio_to_text(audio_file: BytesIO) -> str:
    recognizer = sr.Recognizer()
    try:
        # تحويل الصوت إلى تنسيق WAV باستخدام pydub
        audio = AudioSegment.from_file(audio_file, format='mp4')  # تأكد من تنسيق الصوت
        with BytesIO() as wav_file:
            audio.export(wav_file, format='wav')
            wav_file.seek(0)
            # استخدام SpeechRecognition لتحويل الصوت إلى نص
            audio_data = sr.AudioFile(wav_file)
            with audio_data as source:
                audio_content = recognizer.record(source)
                text = recognizer.recognize_google(audio_content)
        return text
    except Exception as e:
        logger.error(f"Error in audio_to_text: {e}")
        return "Sorry, I could not understand the audio."

# دالة للتعامل مع الأمر /start
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Ask a Question", callback_data='ask')],
        [InlineKeyboardButton("Generate Image", callback_data='image')],
        [InlineKeyboardButton("Get Code", callback_data='code')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Welcome! Please choose an option:",
        reply_markup=reply_markup
    )

# دالة للتعامل مع الأزرار
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'ask':
        query.edit_message_text(text="Use /ask <question> to get an AI response.")
    elif query.data == 'image':
        query.edit_message_text(text="Use /image <description> to get an AI-generated image.")
    elif query.data == 'code':
        query.edit_message_text(text="Use /code <programming question> to get help with programming.")

# دالة للتعامل مع الأمر /ask
def ask(update: Update, context: CallbackContext):
    question = ' '.join(context.args)
    if not question:
        update.message.reply_text("Please provide a question after /ask command.")
        return
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()
        update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Error in /ask command: {e}")
        update.message.reply_text("There was an error processing your request.")

# دالة للتعامل مع الأمر /image
def image(update: Update, context: CallbackContext):
    description = ' '.join(context.args)
    if not description:
        update.message.reply_text("Please provide a description after /image command.")
        return
    
    try:
        response = openai.Image.create(
            prompt=description,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        update.message.reply_photo(photo=image_url)
    except Exception as e:
        logger.error(f"Error in /image command: {e}")
        update.message.reply_text("There was an error processing your request.")

# دالة للتعامل مع الأمر /code
def code(update: Update, context: CallbackContext):
    programming_question = ' '.join(context.args)
    if not programming_question:
        update.message.reply_text("Please provide a programming question after /code command.")
        return
    
    try:
        response = openai.Completion.create(
            model="code-davinci-002",
            prompt=programming_question,
            max_tokens=200,
            temperature=0.2
        )
        code_answer = response.choices[0].text.strip()
        update.message.reply_text(f"Here's the code:\n{code_answer}")
    except Exception as e:
        logger.error(f"Error in /code command: {e}")
        update.message.reply_text("There was an error processing your request.")

# دالة للتعامل مع الرسائل الصوتية
def handle_voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file.download('voice_message.ogg')
    with open('voice_message.ogg', 'rb') as audio_file:
        text = audio_to_text(audio_file)
        update.message.reply_text(f"Transcribed text: {text}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('ask', ask))
    dp.add_handler(CommandHandler('image', image))
    dp.add_handler(CommandHandler('code', code))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))  # إضافة معالجة الرسائل الصوتية
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
