import subprocess


bot_process = subprocess.Popen(["python3", "main.py"])


scheduler_process = subprocess.Popen(["python3", "scheduler.py"])


bot_process.wait()
scheduler_process.wait()
