import os
import time
import re
import threading
import requests
import shutil
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def index():
    return "OTP Bot is running!", 200

@app.route(f"/webhook/{os.environ['TELEGRAM_BOT_TOKEN']}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip().lower()

        if text == "/start":
            send_message(chat_id, "✅ Bot is running and monitoring OTPs!")

        elif text == "/login":
            result = test_login()
            send_message(chat_id, result)

    return {"ok": True}, 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# === Config ===
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
TELEGRAM_USER_ID = os.environ['TELEGRAM_USER_ID']
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
last_sent_otp = None

# === Telegram Send ===
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            print("❌ Telegram Error:", response.status_code, response.text)
        return response.ok
    except Exception as e:
        print("Telegram Exception:", e)
        return False

def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"  # Path to Chromium on Render
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# === OTP Extraction ===
def extract_otp(text):
    match = re.search(r'\b\d{4,8}\b', text)
    return match.group(0) if match else None

def format_message(location, sid, number, otp):
    return f"""
𝑵𝑬𝑾 𝑶𝑻𝑷 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫 🟢

Live SMS - {location}
SID - {sid}
Mobile - {number}
OTP - {otp}

𝑩𝒐𝒕 𝒃𝒚 𝑫𝒆𝒗 | 𝑫𝑿𝒁 𝑾𝒐𝒓𝒌𝒛𝒐𝒏𝒆 𝒊𝒏𝒄.
""".strip()

# === /login Handler ===
def test_login():
    try:
        driver = setup_driver()
        driver.get("https://www.ivasms.com/login")
        time.sleep(2)

        email_input = driver.find_element(By.XPATH, "//input[@type='email']")
        email_input.send_keys(EMAIL)

        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys(PASSWORD)

        remember_checkbox = driver.find_element(By.NAME, "remember")
        if not remember_checkbox.is_selected():
            remember_checkbox.click()

        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        time.sleep(5)

        page_source = driver.page_source
        driver.quit()

        if "Dashboard" in page_source:
            return "✅ Login successful: Dashboard found."
        else:
            return "❌ Login failed: Dashboard not found."

    except Exception as e:
        return f"❌ Error during login: {str(e)}"

# === Main Login + Monitor ===
def main():
    threading.Thread(target=run_flask).start()
    driver = setup_driver()
    try:
        if login(driver):
            monitor_sms(driver)
        else:
            print("❌ Exiting: Login failed.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
