import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Telegram Configuration
TELEGRAM_BOT_TOKEN = '7681288998:AAE9OzduHanSU3drsnAsCmOY2na7af0OVro'
TELEGRAM_CHAT_ID = '1002541578739'

# Login Credentials
EMAIL = 'Unseendevx2@gmail.com'
PASSWORD = 'RheaxDev@2025'

# State memory to avoid duplicate OTPs
last_sent_otp = None

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    return response.ok

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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login(driver):
    driver.get('https://www.ivasms.com/login')
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "remember").click()
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    time.sleep(5)

def monitor_sms(driver):
    global last_sent_otp
    driver.get('https://www.ivasms.com/portal/live/my_sms')
    print("🔍 Monitoring OTPs...")

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
                    formatted = format_message(location, sid, mobile_number, otp)
                    if send_to_telegram(formatted):
                        print(f"✅ Sent OTP: {otp}")
                    else:
                        print("❌ Failed to send to Telegram")

            time.sleep(5)
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(10)
            # Auto relogin if session expired
            login(driver)
            driver.get('https://www.ivasms.com/portal/live/my_sms')

def main():
    driver = setup_driver()
    try:
        login(driver)
        monitor_sms(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()