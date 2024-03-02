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
        ["انتخاب زبان" , "گرفتن لینک های سایت"] ,
        ["درباره"] ,
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


def getlink(text) :
    import requests
    from bs4 import BeautifulSoup as BS
    import re
    def not_lacie(href):
        return href and not re.compile("lacie").search(href)

    final = []
    url = text
    r = requests.get(url)
    content = r.text
    soup = BS(content,'html.parser')
    elem = list(soup.find_all(href=not_lacie))
    count = len(elem)
    for i in range(0,count) :
        li = str(elem[i]).split(" ")
        count2 = len(li)
        for j in range(0,count2) : 
            if "href" in li[j] :
                links = str(li[j]).split("=")
                count3 = len(links)
                for z in range(0,count3) :
                    if str(text).split("//")[1] in links[z] :
                        string = links[z]
                        final.append(string)

    return final


async def getlink_handler (update:Update , context : CallbackContext) :
    links=getlink("https://wikm.ir")
    count = len(links)
    for i in range (0,count) :
        await update.message.reply_text(links[i])

async def send_music_handler(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    with open("your music path", "rb") as music:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
        await context.bot.sendAudio(chat_id, music, caption="آهنگ مورد علاقه من", duration=600, disable_notification=True, timeout=5000)

async def about_handler(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton("سایت ما", callback_data="site"),
            InlineKeyboardButton("تلگرام", callback_data="tel")
        ]
    ]
    await update.message.reply_text(
        text="درباره ما:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def about (update:Update , context : CallbackContext) :
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    if data == "site" :
        text = "سایت انتخاب کردید"
    else :
        text = "تلگرام انتخاب کردید"
    await context.bot.editMessageText(text = text , chat_id = chat_id , message_id = message_id)


def main() :
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start" , start_handler))
    application.add_handler(CommandHandler("sum" , sum_handler))
    application.add_handler(CommandHandler("music" , send_music_handler))

    application.add_handler(CallbackQueryHandler(about))

    application.add_handler(MessageHandler(filters.Regex("انتخاب زبان") , languege_handel))
    application.add_handler(MessageHandler(filters.Regex("بازگشت") , return_handler))
    application.add_handler(MessageHandler(filters.Regex("گرفتن لینک های سایت") , getlink_handler))
    application.add_handler(MessageHandler(filters.Regex("درباره") , about_handler))
    application.run_polling()


main()