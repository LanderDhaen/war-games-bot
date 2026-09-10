import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
HOST_ROLE_ID = os.getenv("HOST_ROLE_ID")