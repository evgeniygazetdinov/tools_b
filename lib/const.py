
import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv("BOT_TOKEN")
URL = "https://api.telegram.org/bot{}/".format(token)
BACKEND_URL = os.getenv("BACKEND_URL")
active_users_path = os.getenv("ACTIVE_USERS_PATH")

if not token:
    raise Exception("BOT_TOKEN not set")