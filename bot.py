import subprocess

# راه اندازی فرآیند برای اجرای فایل bot.py
bot_process = subprocess.Popen(["python3", "main.py"])

# راه اندازی فرآیند برای اجرای فایل scheduler.py
scheduler_process = subprocess.Popen(["python3", "scheduler.py"])

# انتظار برای پایان هر دو فرآیند
bot_process.wait()
scheduler_process.wait()
