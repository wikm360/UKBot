import requests
import schedule
import time

Token = "7029093646:AAFqi8sFOTpJS_t-7GKYRLVZOuyajJa2xWw"

def send_message () :
    global Token
    requests.get("https://api.telegram.org/bot" + Token + "/sendMessage" + "?chat_id=" + "877591460" + "&text=" + "برای هفته آینده غذا رزرو کنید")


def schedule_part() :
    schedule.every().tuesday.at("19:57").do(send_message)
    while True :
        schedule.run_pending()
        # time.sleep(1)

schedule_part()