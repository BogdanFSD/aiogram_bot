import os
import openai
from aiogram import Bot, Router
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
API_TOKEN = os.environ.get("API_TOKEN")


bot = Bot(token="API_TOKEN")
router = Router()
openai.api_key = OPENAI_API_KEY
