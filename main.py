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
import mysql.connector
import subprocess
import requests
import logging
from databasedetail import user_input , password_input , host_input , database_input , token
import schedule
from pytz import timezone
import time
from datetime import datetime
import threading

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

status = bool
list_users = []
date = []
# admin interface :
async def admin_handler (update : Update , context : CallbackContext) :
    admin_chat = 877591460
    chat_id = update.message.chat_id
    if chat_id == admin_chat :
        await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
        await context.bot.sendMessage(chat_id , "سلام گلم . به محیط ادمین خوش آمدی")
        buttons = [
            [
                InlineKeyboardButton("ارسال بکاپ" , callback_data="send_backup")
            ],
            [
                InlineKeyboardButton("ارسال پیام همگانی" , callback_data="send_to_all")
            ],
            [
                InlineKeyboardButton("حذف و اضافه کردن تاریخ" , callback_data="delete_add_date")
            ],
            [
                InlineKeyboardButton("اضافه کردن تاریخ جدید" , callback_data="add_date")
            ]
        ]
        await update.message.reply_text(
            text="منو ادمین" ,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def query_handler(update : Update , context : CallbackContext) :
    global user_input , password_input , database_input , status
    admin_chat = 877591460
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    chat_id_str = str(chat_id)
    if data == "send_backup" :
        if chat_id == admin_chat :
            with open("./backup_file", 'wb') as file:
                subprocess.run(['mysqldump', '-u', user_input, '-p' + password_input, database_input], stdout=file)
            with open ("./backup_file" , "rb") as file :
                await context.bot.send_chat_action(chat_id , ChatAction.UPLOAD_DOCUMENT)
                await context.bot.send_document(chat_id , file , caption="BackUp File" , connect_timeout = 5000)
        await admin_handler(query , context)
    elif data == "send_to_all" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید : ")
        context.user_data['action'] = 'send'
    elif data == "change_status" :
        if status == True :
            db = mysql.connector.connect(user=user_input, password=password_input,
                              host=host_input , database = database_input)
            cursor = db.cursor()
            query = "DELETE FROM users WHERE chat_id = " + chat_id_str
            cursor.execute(query)
            db.commit()
            await context.bot.sendMessage(chat_id , "ربات برای شما غیرفعال شد")
            status = False
        elif status == False :
            db = mysql.connector.connect(user=user_input, password=password_input,
                              host=host_input , database = database_input)
            cursor = db.cursor()
            fisrname = query.message.chat.first_name
            lastname = query.message.chat.last_name
            if fisrname == None :
                fisrname = " "
            if lastname == None :
                lastname = " "
            query = "INSERT INTO users (name, chat_id) VALUES (%s, %s)"
            values = (fisrname+" " + lastname, chat_id)
            cursor.execute(query, values)
            db.commit()
            status = True
            await context.bot.sendMessage(chat_id , "ربات برای شما فعال شد")
            #await start(query , context)
    elif data == "delete_add_date" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید :\n YY-MM-DD , Event ")
        context.user_data['action'] = 'rewrite_dates'
    elif data == "add_date" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید :\n YY-MM-DD , Event ")
        context.user_data['action'] = 'append_dates'

def get_from_db() :
    global user_input , password_input , host_input , database_input
    db = mysql.connector.connect(user=user_input, password=password_input,
                                host=host_input , database = database_input)
    cursor = db.cursor()
    global list_users

    query = "SELECT chat_id FROM users"
    ## getting records from the table
    cursor.execute(query)
    ## fetching all records from the 'cursor' object
    records = cursor.fetchall()
    list_users.clear()
    for record in records:
        list_users.append(str(record).split("(")[1].split(")")[0].split(",")[0].split("'")[1])
    return list_users

async def text_handler (update : Update , context : CallbackContext) :
    global token
    chat_id = update.message.chat_id
    if context.user_data['action'] == "send" :
        text = update.message.text
        context.user_data['action'] = " "
        get_from_db()
        for user in list_users :
            requests.get("https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user + "&text=" + text)
        list_users.clear()
        await context.bot.sendMessage(chat_id , "successful")
    if context.user_data['action'] == "rewrite_dates" :
        text = update.message.text
        context.user_data['action'] = " "
        with open ("./test.txt" , "w") as file :
            file.write(text)
            await context.bot.sendMessage(chat_id , "successful")
    if context.user_data['action'] == "append_dates" :
        text = update.message.text
        context.user_data['action'] = " "
        with open ("./test.txt" , "a") as file :
            file.write("\n" + text)
            await context.bot.sendMessage(chat_id , "successful")


#start and user interface:
        
async def start (update : Update , context : CallbackContext) :
    db = mysql.connector.connect(user=user_input, password=password_input,
                              host=host_input , database = database_input)
    cursor = db.cursor()
    global status
    chat_id = update.message.chat_id
    fisrname = update.message.chat.first_name
    lastname = update.message.chat.last_name
    if fisrname == None :
        fisrname = " "
    if lastname == None :
        lastname = " "
    status_check_in_database(chat_id)
    if status == False :
        query = "INSERT INTO users (name, chat_id) VALUES (%s, %s)"
        values = (fisrname+" " + lastname, chat_id)
        cursor.execute(query, values)
        db.commit()
        await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
        await context.bot.sendMessage(chat_id , " سلام " + str(fisrname) + " " + str(lastname) + "خوش آمدی")
        await context.bot.sendMessage(chat_id , "بات با موفقیت برای شما فعال شد")
    await user_menu(update , context)

async def user_menu(update : Update , context : CallbackContext) :
    buttons = [
        ["مشاهده وضعیت"],
        ["تقویم آموزشی ترم"],
        ["ویژگی های ربات"],
        ["درباره"]
    ]
    await update.message.reply_text(text="منو اصلی :" , reply_markup=ReplyKeyboardMarkup(buttons , resize_keyboard=True))

async def send_calendar(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    with open ("./calendar.jpg" , "rb") as file :
        await context.bot.send_chat_action(chat_id , ChatAction.UPLOAD_PHOTO)
        await context.bot.sendPhoto(chat_id , file , caption="تقویم آموزشی" , connect_timeout = 5000)

async def Features(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    await context.bot.sendMessage(chat_id , '''ویژگی های ربات : \n 
    ۱-ارسال پیام هفتگی برای رزرو غدا هر چهارشنبه \n 
    ۲-ارسال پیام یادآوری در مواقع خاص مانند : \n
        -انتخاب واحد اصلی \n
        -انتخاب واحد مقدماتی \n
        -نظرسنجی اساتید \n
        -حذف اضطراری تک درس \n
-نظرسنجی استاد راهنما\n
        \n''')

async def about(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    await context.bot.sendMessage(chat_id , "Created By @wikm360 with ❤️ \n V2.1" )

def status_check_in_database(chat_id) :
    db = mysql.connector.connect(user=user_input, password=password_input,
                              host=host_input , database = database_input)
    cursor = db.cursor()
    global status
    status = False
    chat_id_str = str(chat_id)
    query = "SELECT * FROM users"
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        if record[2] == chat_id_str :
            status = True
            break
        else :
            pass


async def status_check(update : Update , context : CallbackContext) :
    global status
    chat_id = update.message.chat_id
    status_check_in_database(chat_id)
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
        text="عملیات :" ,
        reply_markup=InlineKeyboardMarkup(buttons)) #request send to query handler
    
####################scheduler######################
def send_message_every () :
    global token
    global list_users
    get_from_db()
    print(list_users)
    for user in list_users :
        requests.get("https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user + "&text=" + "برای هفته آینده غذا رزرو کنید")
    list_users.clear()

def send_message_specific () :
    global token
    global list_users
    global date
    get_from_db()
    with open ("./date.txt" , "r") as file :
        for line in file :
            date = line.split(",")[0].strip()
            event = line.split(",")[1].strip()
            specific_date = datetime.strptime(date, '%Y-%m-%d') 
            current_date = datetime.now()
            if specific_date.date() == current_date.date():
                for user in list_users :
                    requests.get("https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user + "&text=" + " یادآوری " + event)
                list_users.clear()
            list_users.clear()

def send_backup () : 
    global token
    admin_chat = '877591460'
    with open("./backup_file", 'wb') as file:
        subprocess.run(['mysqldump', '-u', user_input, '-p' + password_input, database_input], stdout=file)
    url = f'https://api.telegram.org/bot{token}/sendDocument'
    with open("./backup_file", 'rb') as file:
        files = {'document': file}
        data = {'chat_id': admin_chat}
        response = requests.get(url, files=files, data=data)
    
    print(response.json())

def schedule_message() :
    schedule.every().wednesday.at("09:00" , timezone("Asia/Tehran")).do(send_message_every)
    schedule.every().day.at("08:00" , timezone("Asia/Tehran")).do(send_message_specific)
    schedule.every().day.at("23:00" , timezone("Asia/Tehran")).do(send_backup)

    while True:
        schedule.run_pending()
        time.sleep(1)

async def error(update:Update , context : CallbackContext) :
    logging.warning('Update "%s" caused error "%s"', update, context.error)

def main () :
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start" , start))
    application.add_handler(CommandHandler("admin" , admin_handler))

    application.add_handler(CallbackQueryHandler(query_handler))

    application.add_handler(MessageHandler(filters.Regex("تقویم آموزشی ترم") , send_calendar))
    application.add_handler(MessageHandler(filters.Regex("مشاهده وضعیت") , status_check))
    application.add_handler(MessageHandler(filters.Regex("ویژگی های ربات") , Features))
    application.add_handler(MessageHandler(filters.Regex("درباره") , about))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , text_handler))

    application.add_error_handler(error)

    schedule_thread = threading.Thread(target=schedule_message)
    schedule_thread.start()

    application.run_polling()


main()
