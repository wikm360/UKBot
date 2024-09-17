
# UKBot

Telegram bot, food reservation reminder and educational calendar dates reminder.


Adding automatic log-in and food reservations on the Cullinan site soon


🟢 Example - Shahid Bahonar University of Kerman : https://t.me/ukcalendar_bot


## Installation


First of all , Download and Unzip file :

```bash
    wget https://github.com/wikm360/UKBot/releases/latest/download/UKBot.zip
    mkdir UKBot
    unzip UKBot.zip -d UKBot
    cd UKBot
```

install requirements python library :

```bash
    pip install -r requirements.txt

```

## Change Variables 

change Variable with your own :


```bash
    nano Variables.py
    nano date.txt

```
Also change calendar.jpg image with your educational calendar


## Mysql Setup 

After install mysql and change Variables , run this :


```bash
    sudo python3 mysql_setup.py

```



## Start

For start Bot :


```bash
    sudo python3 main.py

```
