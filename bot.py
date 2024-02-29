from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler , Updater , CallbackContext
from telegram import Update
from telegram.constants import ChatAction
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler
from telegram.ext.filters import BaseFilter
token = "6906320146:AAGRtpszj4HqM9r-KEPaYklswuxshMfB1PA"

async def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    firstname = update.message.chat.first_name
    lastname = update.message.chat.last_name
    #  اکشن ایز تایپینگ
    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    # دو روش برای ارسال پیام
    #await context.bot.sendMessage(chat_id, " سلام گلم"+firstname+" "+ lastname)
    await update.message.reply_text("سلام گلم " + firstname + " " + lastname)
    # صدا زدن کیبورد های منو اصلی
    await main_menu_handler(update , context)

async def sum_handler(update: Update , context: CallbackContext):
    chat_id = update.message.chat_id
    # گرفتن آرگومان های جلوی کامند و ریختنشون توی یک متغییر
    numbers = context.args
    # تبدیل اعداد گرفته شده توی لیست به اینتیجر
    result = sum(int(i) for i in numbers)
    await context.bot.send_chat_action(chat_id,ChatAction.TYPING)
    await update.message.reply_text("مجموع اعداد برابر = " + str(result))

async def main_menu_handler(update:Update , context : CallbackContext) :
    buttons = [
        ["انتخاب زبان" , "گزینه دوم"] ,
        ["گزینه سوم"] ,
        ["گزینه چهارم"]
    ]
    # یک ورودی دیگه ای که کیبورد مارکاپ میشه بهش داد برای اینکه هروقت یک گزینه زد کیبورد بره پایین :
    # one_time_keyboard=True
    await update.message.reply_text(text="منو اصلی" , reply_markup=ReplyKeyboardMarkup(buttons , resize_keyboard=True))

async def languege_handel (update : Update , context : CallbackContext) :
    buttons = [
        ["پایتون" , "کاتلین"],
        ["سی پلاس پلاس"],
        ["بازگشت"]
    ]
    await update.message.reply_text(text="زبان خود را انتخاب کنید :" , reply_markup=ReplyKeyboardMarkup(buttons , resize_keyboard=True))

async def return_handler (update : Update , context : CallbackContext) : 
    await main_menu_handler(update , context)

def main() :
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start" , start_handler))
    application.add_handler(CommandHandler("sum" , sum_handler))
    application.add_handler(MessageHandler(BaseFilter("انتخاب زبان") , languege_handel))
    application.add_handler(MessageHandler(BaseFilter("بازگشت") , return_handler))

    application.run_polling()


main()