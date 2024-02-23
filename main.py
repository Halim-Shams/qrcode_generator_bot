import os
from threading import Timer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import qrcode
import numpy as np
from dotenv import load_dotenv, dotenv_values
import cv2, urllib.request

load_dotenv()


API_TOKEN = os.getenv("API_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Qrcode generator
def qrcode_generator(text: str):
    qrcode_img = qrcode.make(text)
    qrcode_img.save('qr.png')  
    
# Qrcode detector/reader 
def qr_detector(url):
    try:
        url_response = urllib.request.urlopen(url)
        img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
        img_byte = cv2.imdecode(img_array, -1)
        img = img_byte
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(img)
        return value
    except:
        return
        
     
# Delete the photo
def delete():
    os.remove('qr.png')

# Delete photo after 3sec
def delete_photo():
    t = Timer(3.0, delete)
    t.start()


# /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hey dear {update.effective_user.first_name}, send me a text or link to hand you a Qrcode in return.')
    

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text ='''
/start - For starting the bot.
/help - For how to use this bot.
'''
    await update.message.reply_text(help_text)
    
    
# handle reply
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    
    if update.message.photo:
        photo = update.message.photo[0]
        await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action='typing')
        print('photo detected')
        file_id = photo.file_id
        file_path = await context.bot.get_file(file_id=file_id)
        qrcode_photo = file_path.file_path
        decoded_data = qr_detector(qrcode_photo)
        print(decoded_data)
        await update.message.reply_text(decoded_data, reply_to_message_id=update.message.message_id)
        
    elif update.message.text:
        text = update.message.text
        print('text detected')
        if message_type == 'supergroup':
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action='upload_photo')
            if BOT_USERNAME in text:
                new_text = text.replace(BOT_USERNAME, '').strip()
                qrcode_generator(new_text)
                await update.message.reply_photo('qr.png')
                delete_photo()
            else:
                return
        else:
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action='upload_photo')
            qrcode_generator(text)
            await update.message.reply_photo('qr.png')
            delete_photo()
    
        


if __name__ == '__main__':
    print('Starting bot...')
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.ALL, handle_reply))
    print('Polling...')
    app.run_polling()