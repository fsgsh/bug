from telethon import TelegramClient
from .config import Config
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

config = Config()
bot = TelegramClient("aurora", config.telegram.api_id,
                     config.telegram.api_hash)
bot.start(bot_token=config.telegram.token)
