from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler , Updater , CallbackContext
from telegram import Update
from telegram.constants import ChatAction
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler

token = "7029093646:AAFqi8sFOTpJS_t-7GKYRLVZOuyajJa2xWw"
status = bool
# admin interface :
async def admin_handler (update : Update , context : CallbackContext) :
    admin_chat = 877591460
    chat_id = update.message.chat_id
    if chat_id == admin_chat :
        await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
        #######################print(update)
        await context.bot.sendMessage(chat_id , "سلام گلم . به محیط ادمین خوش آمدی")
        buttons = [
            [
                InlineKeyboardButton("ارسال بکاپ" , callback_data="send_backup"),
                InlineKeyboardButton("ارسال پیام همگانی" , callback_data="send_to_all")
            ]
        ]
        await update.message.reply_text(
            text="منو ادمین" ,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def query_handler(update : Update , context : CallbackContext) :
    global status
    admin_chat = 877591460
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    if data == "send_backup" :
        if chat_id == admin_chat :
            with open ("./id.txt" , "rb") as file :
                await context.bot.send_chat_action(chat_id , ChatAction.UPLOAD_DOCUMENT)
                await context.bot.send_document(chat_id , file , caption="BackUp File" , connect_timeout = 5000)
        await admin_handler(query , context)
    elif data == "send_to_all" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید : ")
        context.user_data['action'] = 'send'
    elif data == "change_status" :
        if status == True :
            chat_id_str = str(chat_id)
            with open("./id.txt" , "r+") as file :
                for line in file :
                    id = line.strip()
                    if id == chat_id_str :
                        del file(line)


async def text_handler (update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    if context.user_data['action'] == "send" :
        name = update.message.text
        await context.bot.sendMessage(chat_id , name)
        context.user_data['action'] = " "

#start and user interface:
        
async def start (update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    fisrname = update.message.chat.first_name
    lastname = update.message.chat.last_name
    if fisrname == None :
        fisrname = " "
    if lastname == None :
        lastname = " "
    
    with open("./id.txt" , "a" ) as file :
        file.write(str(chat_id)+"\n")
    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    await context.bot.sendMessage(chat_id , " سلام " + str(fisrname) + " " + str(lastname))
    await context.bot.sendMessage(chat_id , "بات با موفقیت برای شما فعال شد")
    await user_menu(update , context)

async def user_menu(update : Update , context : CallbackContext) :
    buttons = [
        ["مشاهده وضعیت"] ,
        ["درباره"]
    ]
    # یک ورودی دیگه ای که کیبورد مارکاپ میشه بهش داد برای اینکه هروقت یک گزینه زد کیبورد بره پایین :
    # one_time_keyboard=True
    await update.message.reply_text(text="منو اصلی" , reply_markup=ReplyKeyboardMarkup(buttons , resize_keyboard=True))

async def status_check(update : Update , context : CallbackContext) :
    global status
    status = False
    chat_id = update.message.chat_id
    chat_id_str = str(chat_id)
    with open("./id.txt" , "r") as file :
        for line in file :
            id = line.strip()
            if id == chat_id_str :
                status = True
                break
            else :
                pass
    if status == True :
        await context.bot.sendMessage(chat_id , "ربات برای شما فعال میباشد")
    elif status == False :
        await context.bot.sendMessage(chat_id , "ربات برای شما فعال نمیباشد")
    buttons = [
            [
                InlineKeyboardButton("تغییر وضعیت" , callback_data="change_status")
            ]
        ]
    await update.message.reply_text(
        text="منو" ,
        reply_markup=InlineKeyboardMarkup(buttons))

def set () :
    unilist = []
    list = []
    with open("./id.txt" , "r") as file :
        for line in file :
            id = line.strip()
            list.append(id)
        unilist = set(list)
    with open ("./id.txt" , "w") as file :
        for i in unilist :
            file.write(i + "\n") 

def main () :
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start" , start))
    application.add_handler(CommandHandler("admin" , admin_handler))

    application.add_handler(CallbackQueryHandler(query_handler))

    application.add_handler(MessageHandler(filters.Regex("مشاهده وضعیت") , status_check))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , text_handler))

    application.run_polling()


main()
