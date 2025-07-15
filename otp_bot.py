# === Config ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

# Print the values for debugging (remove this in production)
print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
print("TELEGRAM_CHAT_ID:", TELEGRAM_CHAT_ID)
print("TELEGRAM_USER_ID:", TELEGRAM_USER_ID)
print("EMAIL:", EMAIL)
print("PASSWORD:", PASSWORD)

# Check if the required environment variables are set
if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_USER_ID, EMAIL, PASSWORD]):
    raise ValueError("One or more environment variables are not set. Please check your configuration.")
