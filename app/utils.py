import asyncio
import json
import os
from dotenv import load_dotenv
import requests

DATA_FILE = "listings.json"
load_dotenv()

def load_listings():
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return set(data)

def save_listings(listings):
    with open(DATA_FILE, "w") as f:
        json.dump(list(listings), f)

def send_telegram(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.json()

# Load/save subscribers
def load_subscribers():
    try:
        with open("subscribers.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_subscribers(subscribers):
    with open("subscribers.json", "w") as file:
        json.dump(subscribers, file)

# Add a new subscriber
async def add_subscriber(chat_id):
    subscribers = load_subscribers()
    if chat_id not in subscribers:
        subscribers.append(chat_id)
        save_subscribers(subscribers)

# Remove subscriber
def remove_subscriber(chat_id):
    subscribers = load_subscribers()
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)
        print(f"Subscriber {chat_id} removed.")

async def broadcast_message(message):
    subscribers = load_subscribers()
    for chat_id in subscribers:
        await send_telegram(message, chat_id)

# Send a message to a specific user
async def send_telegram(message, chat_id):
    url = f'https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)

# Listen for updates (messages sent to the bot)
async def get_updates():
    url = f'https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/getUpdates'
    response = requests.get(url)
    updates = response.json()['result']

    for update in updates:
        chat_id = update['message']['chat']['id']
        message_text = update['message']['text']

        # If the message is '/start', add the user to the list
        if message_text == "/start":
            await add_subscriber(chat_id)

        # You can handle other commands or actions here
        # Example: if message_text == "/unsubscribe", call remove_subscriber(chat_id)

# Call this function periodically (e.g., every minute) to check for new messages and subscribers.

async def safe_goto(page, url, retries=3, wait_for="networkidle"):
    for attempt in range(retries):
        try:
            await page.goto(url)
            await page.wait_for_load_state(wait_for)
            if page.url != url:
                raise Exception(f"Unexpected redirect: {page.url}")
            return
        except Exception as e:
            print(f"[!] Error loading page (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                raise
            await asyncio.sleep(5)  # wait before retry