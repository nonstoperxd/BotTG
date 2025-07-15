import time
import re
import threading
import requests
import os
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

@app.route(f"/webhook/7681288998:AAE9OzduHanSU3drsnAsCmOY2na7af0OVro", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text.strip().lower() == "/start":
            send_message(chat_id, "✅ Bot is running and monitoring OTPs!")
    return {"ok": True}, 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# === Config ===
TELEGRAM_BOT_TOKEN = "7681288998:AAE9OzduHanSU3drsnAsCmOY2na7af0OVro"
TELEGRAM_CHAT_ID = "-1002541578739"
WEBHOOK_URL = f"https://bottg-4mz8.onrender.com/webhook/{TELEGRAM_BOT_TOKEN}"

EMAIL = 'Unseendevx2@gmail.com'
PASSWORD = 'RheaxDev@2025'
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

def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    response = requests.post(url, data={"url": WEBHOOK_URL})
    if response.ok:
        print("✅ Webhook set successfully.")
    else:
        print("❌ Webhook failed:", response.text)

# === OTP Monitoring ===
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

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def login(driver):
    print("🔐 Logging into IVASMS...")
    driver.get('https://www.ivasms.com/login')
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

    # ✅ Check if redirected page contains "Dashboard"
    if "Dashboard" in driver.page_source:
        print("✅ Login successful — 'Dashboard' found.")
        return True
    else:
        print("❌ Login failed — 'Dashboard' not found.")
        send_message(TELEGRAM_CHAT_ID, "❌ *Login to IVASMS failed.* Please check credentials or site status.")
        return False

def monitor_sms(driver):
    global last_sent_otp
    driver.get('https://www.ivasms.com/portal/live/my_sms')
    print("📡 Monitoring OTPs...")

    while True:
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 5:
                    continue

                location = cols[0].text.strip()
                sid = cols[1].text.strip()
                message = cols[3].text.strip()
                mobile_number = cols[4].text.strip()

                otp = extract_otp(message)
                if otp and otp != last_sent_otp:
                    last_sent_otp = otp
                    msg = format_message(location, sid, mobile_number, otp)
                    if send_message(TELEGRAM_CHAT_ID, msg):
                        print(f"✅ OTP Sent: {otp}")
                    else:
                        print("❌ Failed to send OTP")
            time.sleep(5)
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(10)
            if login(driver):
                driver.get('https://www.ivasms.com/portal/live/my_sms')
            else:
                print("❌ Stopping monitor due to failed re-login.")
                break

def main():
    set_webhook()
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
