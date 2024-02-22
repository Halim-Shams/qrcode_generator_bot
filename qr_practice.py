import os
from threading import Timer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import qrcode



API_TOKEN = '5487417291:AAGEKMm2IRpt83B0EKC8CFoLs_y3bbvTfFE'
BOT_USERNAME = '@halim_bunny_bot'

# Qrcode generator
def qrcode_generator(text: str):
    qrcode_img = qrcode.make(text)
    qrcode_img.save('qr.png')  
     

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
    text = update.message.text
    
    if message_type == 'supergroup':
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
    app.add_handler(MessageHandler(filters.TEXT, handle_reply))
    print('Polling...')
    app.run_polling()