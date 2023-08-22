import logging, os, time, glob
from telegram import Update

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.disable())


logger = logging.getLogger(__name__)

def getTime():
    millis = int(round(time.time() * 1000))
    return millis

def echo(update, context):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    if str(chatid)[0] != '-' and chatid != 518091838:
        context.bot.send_message(chat_id=update.message.chat_id, text="To start using this bot, drop a blackbox logging file.")
    return
    
def file(update: Update, context):
    message = update.message
    document = message.document
    
    try:
        caption = message.caption

        if not caption:
            bypass_filesize = False
        else:
            caption = caption.lower()
            if ("bypass" in caption and "size" in caption) or ("ignorar" in caption and "tamaño" in caption) or ("ignore" in caption and ("file" in caption or "size" in caption)):
                bypass_filesize = True
            else:
                bypass_filesize = False

    except Exception as e:
        print(str(e))
        bypass_filesize = False

    updateId = update.update_id
    messageId = message.message_id
    fileId = document.file_id

    name = document.file_name
    mime = document.mime_type
    size = document.file_size
    
  
    user = message.from_user.username
    actualTime = getTime()

    if (user != None): 
        fileName = user + "_" + str(actualTime) + ".BBL"
    else:
        fileName = str(actualTime) + ".BBL"

    if (mime != "text/plain") and (mime != "application/octet-stream") and (mime != "null") and (mime != None):
        return
    if (name[-4:] != ".BBL") and (name[-4:] != ".bbl") and (name[-4:] != ".BFL") and (name[-4:] != ".bfl"):
        return
    min_size = 3.5 * 1024 * 1024
    max_size = 14 * 1024 * 1024

    size_mb = round((size / 1024 / 1024), 2)
    if size < min_size and bypass_filesize == False:
        message.reply_text(f"File size error.\n{size_mb}MB is too low. The minimum accepted is 3.5MB.")
        return
    elif size > max_size and bypass_filesize == False:
        message.reply_text(f"File size error.\n{size_mb}MB is too high. The maximum accepted is 14MB.")
        return
    else:
        file = context.bot.get_file(fileId)
        customPath = "downloads/" + fileName
        file.download(custom_path=customPath)
        try:
            if bypass_filesize == True and size < min_size:
                message.reply_text(f"""⚠️⚠️⚠️  
The blackbox file you sent is {size_mb}MB which is too low. It _can_ lead to *unreliable data*, please be careful when interpreting the results.  
⚠️⚠️⚠️""", parse_mode=ParseMode.MARKDOWN)
            else:
                message.reply_text("File has been downloaded. Starting PID Analyzer. It can take up a few minutes, be patient.")
        except Exception as e:
            print(e)
        #os.system("py PID-Analyzer.py --log " + customPath + " --name " + str(user) + " --s N")
        os.system("PID-Analyzer_0.52.exe --log " + customPath + " --name " + str(user) + " --s N")

        images = glob.glob("downloads\\" + str(user) + "\\" + user + "_" + str(actualTime) + "*.png")
        for image in images:
            message.reply_photo(photo=open(image, "rb"))
            os.system("del " + str(image))
        os.system("del downloads\\" + fileName)
        os.system("del downloads\\" + str(user) + " /q /f")
        os.system("rmdir downloads\\" + str(user))


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', bot, update.error)

def main():
    """Start the bot."""
    updater = Updater("",use_context=True)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.document, file))

    dp.add_error_handler(error)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()