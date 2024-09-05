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
from mysql.connector import Error
import subprocess
import requests
import logging
from Variables import user_input , password_input , host_input , database_input , token , port_mysql , admin_chat
import schedule
from pytz import timezone
import time
import datetime
import threading
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote_plus
import time
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import asyncio

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

status = bool
list_users = []
date = []

def connect_to_database():
    try:
        db = mysql.connector.connect(user=user_input, password=password_input,
                            host=host_input , database = database_input ,port  = port_mysql)

        if db.is_connected():
            print("Connected to MySQL database")
            return db
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# admin interface :
async def admin_handler (update : Update , context : CallbackContext) :
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
    global status
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
            db = connect_to_database()
            cursor = db.cursor()
            query = "DELETE FROM users WHERE chat_id = " + chat_id_str
            cursor.execute(query)
            db.commit()
            db.close()
            await context.bot.sendMessage(chat_id , "ربات برای شما غیرفعال شد")
            status = False
        elif status == False :
            db = connect_to_database()
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
            db.close()
            status = True
            await context.bot.sendMessage(chat_id , "ربات برای شما فعال شد")
            #await start(query , context)
    elif data == "delete_add_date" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید :\n YY-MM-DD , Event ")
        context.user_data['action'] = 'rewrite_dates'
    elif data == "add_date" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید :\n YY-MM-DD , Event ")
        context.user_data['action'] = 'append_dates'
    elif data == "confirm" :
        get_from_db()
        db = connect_to_database()
        cursor = db.cursor()

        global list_users
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        if user_id in list_users :
            query = f"""
            UPDATE users
            SET last_reminder = %s
            WHERE chat_id = %s
        """
            values = (None , chat_id)
            cursor.execute(query, values)
            db.commit()
            db.close()
            await context.bot.sendMessage(user_id , "یادآوری تایید شد. ممنون!")


def get_from_db() :
    db = connect_to_database()
    cursor = db.cursor()
    global list_users
    
    query = "SELECT chat_id FROM users"
    ## getting records from the table
    cursor.execute(query)
    ## fetching all records from the 'cursor' object
    records = cursor.fetchall()
    list_users.clear()
    for record in records:
        try :
            r = str(record).split("(")[1].split(")")[0].split(",")[0].split("'")[1]
            list_users.append(r)
        except :
            pass
    db.close()
    return list_users

async def text_handler (update : Update , context : CallbackContext) :

    if 'next_step' in context.user_data:
            next_step = context.user_data['next_step']
            if next_step == 'get_username':
                del context.user_data['next_step']  # پاک کردن وضعیت بعد از اجرا
                await get_username(update, context)
            if next_step == 'get_password':
                del context.user_data['next_step']  # پاک کردن وضعیت بعد از اجرا
                await get_password(update, context)
                
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
    db = connect_to_database()
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
        db.close()
        await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
        await context.bot.sendMessage(chat_id , " سلام " + str(fisrname) + " " + str(lastname) + "خوش آمدی")
        await context.bot.sendMessage(chat_id , "بات با موفقیت برای شما فعال شد")
        feauture = '''ویژگی های ربات : \n 
    ۱-ارسال پیام هفتگی برای رزرو غدا هر چهارشنبه \n 
    ۲-ارسال پیام یادآوری در مواقع خاص مانند : \n
        -انتخاب واحد اصلی \n
        -انتخاب واحد مقدماتی \n
        -نظرسنجی اساتید \n
        -حذف اضطراری تک درس \n
        - نظر سنجی اساتید \n
        - به زودی امکان رزرو خودکار غذا بر اساس اولویت شما در کالینان
        '''
        await context.bot.sendMessage(chat_id , feauture)
    await user_menu(update , context)

async def user_menu(update : Update , context : CallbackContext) :
    buttons = [
        ["مشاهده وضعیت" , "تقویم آموزشی ترم"],
        ["ویژگی های ربات"],
        ["تنظیم کالینان"],
        ["درباره"],
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
        - نظر سنجی اساتید \n
        - به زودی امکان رزرو خودکار غذا بر اساس اولویت شما در کالینان
        ''')


async def setnut (update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    await context.bot.sendMessage(chat_id , text="در این بخش با تنظیم کردن یوزرنیم و پسورد اکانت کالینان خود ، در آپدیت بعدی امکان رزرو خودکار غذا شما در سایت کالینان از طریق بات بر اساس اولویت شما امکان پذیر میشود")
    await context.bot.sendMessage(chat_id , text="لطفاً یوزرنیم خود را وارد کنید:")
    context.user_data['next_step'] = 'get_username'


async def get_username(update : Update , context : CallbackContext):
    chat_id = update.message.chat_id
    # دریافت یوزرنیم از کاربر
    username = update.message.text
    await context.bot.sendMessage(chat_id , text=f"username = {username}")

    # ذخیره یوزرنیم در متغیر
    context.user_data['username'] = username
    
    # درخواست پسورد از کاربر
    await context.bot.sendMessage(chat_id , text="لطفاً پسورد خود را وارد کنید:")
    context.user_data['next_step'] = 'get_password'

# تابع دریافت پسورد
async def get_password(update : Update , context : CallbackContext):
    chat_id = update.message.chat_id
    # دریافت پسورد از کاربر
    password = update.message.text
    
    # ذخیره پسورد در متغیر
    context.user_data['password'] = password

    db = connect_to_database()
    cursor = db.cursor()
    query = f"""
    UPDATE users
    SET nut_username = %s, nut_password = %s
    WHERE chat_id = %s
"""
    values = (context.user_data['username'], password ,  chat_id)
    cursor.execute(query, values)
    db.commit()
    db.close()
    
    # ارسال یوزرنیم و پسورد به کاربر
    await context.bot.sendMessage(chat_id , text=f"username = {context.user_data['username']}  , password = {password} ✅")
    
    await start(update, context)

def selenium ( max_retries, retry_delay , user , passwd , chat_id) :
    attempt = 0
    while attempt < max_retries:
        try:
            chrome_options = Options()
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')

            chrome_options.add_argument('--disable-dev-shm-usage')

            # Start a new instance of Chrome web browser
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()) , options=chrome_options)
            # driver = webdriver.Chrome()


            # Open the website
            driver.get("https://nut.uk.ac.ir/")


            # Find and click username
            try:
                time.sleep(5)
                username = driver.find_element(By.ID,"txtUsernamePlain")
                username.click()
                username.clear()
                username.click()
                username.send_keys(user)
                time.sleep(1)
            except:
                pass

            # specific_option = driver.find_element(By.XPATH,type)
            # specific_option.click()

            # Find and click username
            password = driver.find_element(By.ID,"txtPasswordPlain")
            password.click()
            password.clear()
            password.click()
            password.send_keys(passwd)
            time.sleep(1)

            #capcha
            captcha_element = driver.find_element(By.ID,"Img1")
            captcha_image = captcha_element.screenshot_as_png
            with open(f"captcha_{chat_id}.png", "wb") as f:
                f.write(captcha_image)
            time.sleep(5)
            image_path = f"captcha_{chat_id}.png"
            captcha_text = extract_text_from_image(image_path)

            capcha = driver.find_element(By.ID,"txtCaptcha")
            capcha.click()
            capcha.clear()
            capcha.click()
            capcha.send_keys(captcha_text)
            time.sleep(5)

            #submit
            done = driver.find_element(By.ID,'btnEncript')
            done.click()
            time.sleep(5)
            
            # finde error element
            try:
                error_element = driver.find_element(By.ID, "lblLoginError")
                error_text = error_element.text
                if error_text == "کد امنیتی صحیح نمی باشد":
                    print(f"Error message found: {error_text}")
                    #return True
                else:
                    print("Error message not found or different.")
                    attempt += 3
                    break
                    #return False
            except:
                print("Error element not found on the page.")
                #return False
                attempt += 3
                break

        except Exception as e:
            print(f"An error occurred: {e}")

        attempt += 1
        print(f"Retrying ({attempt}/{max_retries})...")
        time.sleep(retry_delay)

    print("Max retries reached. Exiting.")
    return False

def kalinan () :
    global list_users
    get_from_db()
    for chat_id in list_users :
        db = connect_to_database()
        cursor = db.cursor()
        query = f"SELECT nut_username FROM users WHERE chat_id={chat_id}"
        ## getting records from the table
        cursor.execute(query)
        ## fetching all records from the 'cursor' object
        user_list = cursor.fetchall()
        query = f"SELECT nut_password FROM users WHERE chat_id={chat_id}"    
        cursor.execute(query)
        passwd_list = cursor.fetchall()
        db.close()
        try:
            user = str(user_list[0]).split("(")[1].split(")")[0].split(",")[0].split("'")[1]
            passwd = str(passwd_list[0]).split("(")[1].split(")")[0].split(",")[0].split("'")[1]
        except Exception as e:
            print(f"Error for chat_id {chat_id}: {e}")
            continue
    try:
        success = selenium(3 , 2  , user=user , passwd=passwd, chat_id=chat_id)
        if not success:
            print("No error found or different error. Trying again...")
        else:
            print("Error message handled. Exiting.")
        time.sleep(5)

    finally:
        pass
        

def preprocess_image(image_path , enhance):
    image = Image.open(image_path)
    
    # تبدیل به خاکستری
    image = image.convert('L')
    
    # افزایش کنتراست
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(enhance)
    
    # فیلتر کردن برای حذف نویز
    image = image.filter(ImageFilter.MedianFilter())
    
    return image

def count_digits(num):
    number = int(num)
    if number == 0:
        return 1
    count = 0
    number = abs(number)
    while number > 0:
        number //= 10
        count += 1
    return count

def extract_text_from_image(image_path):
    # پیش‌پردازش تصویر
    enhance = 2.0
    preprocessed_image = preprocess_image(image_path  , enhance)
    
    # استخراج متن از تصویر با استفاده از Tesseract OCR
    text = pytesseract.image_to_string(preprocessed_image, config='--psm 6 digits')  # تنظیم برای تشخیص اعداد
    count = 0
    text.strip()
    while True :
        if count >= 11 :
            break
        try :
            int(text)
            break
        except :
            enhance +=0.1
            preprocessed_image = preprocess_image(image_path , enhance)
            text = pytesseract.image_to_string(preprocessed_image, config='--psm 6 digits')  # تنظیم برای تشخیص اعداد
            count +=1
    while count_digits(text) != 4 :
        print(f"try {count}")
        enhance +=0.1
        preprocessed_image = preprocess_image(image_path , enhance)
        text = pytesseract.image_to_string(preprocessed_image, config='--psm 6 digits')  # تنظیم برای تشخیص اعداد
        text.strip()
        count +=1
        if count >= 11 :
            print("ERORR")
            break
    # چاپ متن استخراج‌شده
    print("Extracted Text:", text)
    return text.strip()


async def about(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    await context.bot.sendMessage(chat_id , "Created By @wikm360 with ❤️ \n V3.5" )

def status_check_in_database(chat_id) :
    db = connect_to_database()
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
    db.close()


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
            specific_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            current_date = datetime.datetime.now()
            if specific_date.date() == current_date.date():
                for user in list_users :
                    requests.get("https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user + "&text=" + " یادآوری " + event)
                list_users.clear()
            list_users.clear()

def send_backup () : 
    global token
    with open("./backup_file", 'wb') as file:
        subprocess.run(['mysqldump', '-u', user_input, '-p' + password_input, database_input], stdout=file)
    url = f'https://api.telegram.org/bot{token}/sendDocument'
    with open("./backup_file", 'rb') as file:
        files = {'document': file}
        data = {'chat_id': admin_chat}
        response = requests.get(url, files=files, data=data)
    
    print(response.json())

async def send_reminder(context :CallbackContext):
    global token
    global list_users
    get_from_db()
    global list_users
    db = connect_to_database()
    cursor = db.cursor()

    tehran_tz = timezone('Asia/Tehran')
    if datetime.datetime.now(tehran_tz).weekday() == 3:  # 3 یعنی پنجشنبه
        for user in list_users :
            query = f"SELECT last_reminder FROM users WHERE chat_id={user}"
            ## getting records from the table
            cursor.execute(query)
            ## fetching all records from the 'cursor' object
            last_reminder = cursor.fetchall()
            print(last_reminder)
            type(last_reminder)

            keyboard = [[InlineKeyboardButton("تایید", callback_data='confirm')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = await context.bot.send_message(
                chat_id=user,
                text="این یک پیام یادآوری است. لطفاً تایید کنید.",
                reply_markup=reply_markup
            )
            query = f"""
            UPDATE users
            SET last_reminder = %s
            WHERE chat_id = %s
        """
            values = (message.message_id , user)
            cursor.execute(query, values)
            db.commit()

    db.close()
    list_users.clear()

    await wait(context)


async def wait (context) :
    print("WAIT")
    await asyncio.sleep(60)
    count = 0
    while True  :
        print(count)
        if count >= 3 :
            break
        await check_reminders(context)
        count += 1
        await asyncio.sleep(60)

async def check_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    print("CHECK")
    global token
    global list_users
    get_from_db()
    global list_users
    db = connect_to_database()
    cursor = db.cursor()
    for user in list_users :
        query = f"SELECT last_reminder FROM users WHERE chat_id={user}"
        ## getting records from the table
        cursor.execute(query)
        ## fetching all records from the 'cursor' object
        last_reminder = cursor.fetchall()
        print(type(last_reminder))
        flag = last_reminder[0][0]
        print(type(flag))
        print(flag)
        if flag:
            print(last_reminder)
            keyboard = [[InlineKeyboardButton("تایید", callback_data='confirm')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=user,
                text="لطفاً یادآوری را تایید کنید.",
                reply_markup=reply_markup
            )
    db.close()
    list_users.clear()

def schedule_message() :
    ##schedule.every().wednesday.at("09:00" , timezone("Asia/Tehran")).do(send_message_every)

    schedule.every().day.at("08:00" , timezone("Asia/Tehran")).do(send_message_specific)
    schedule.every().day.at("23:25" , timezone("Asia/Tehran")).do(send_backup)
    #schedule.every().monday.at("09:00" , timezone("Asia/Tehran")).do(kalinan)

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
    application.add_handler(MessageHandler(filters.Regex("تنظیم کالینان") , setnut))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , text_handler))

    application.add_error_handler(error)

    #send message every wednesday for kalinan :
    # tehran_tz = timezone('Asia/Tehran')
    # time_in_tehran = datetime.time(hour=8, minute=5, tzinfo=tehran_tz)
    # job_queue = application.job_queue
    # job_queue.run_daily(send_reminder, time=time_in_tehran)

    schedule_thread = threading.Thread(target=schedule_message)
    schedule_thread.start()

    application.run_polling()


main()
