import asyncio
import importlib

from telethon import events
from telethon.tl.custom import Button

from . import bot
from .handlers.commandhandler import CommandHandler
from .modules import ALL_MODULES

HELPABLE: str = "**Here is what I can do:\n**"

PM_START_TEXT = \
    """
Hi {}, my name is {}! I'm a Telegram bot made by [this awesome person](https://t.me/nitanmarcel) to help Aurora's groups to manage their groups and keep track of bugs and suggestions sent there.
Read more about AuroraOSS [here](http://auroraoss.com/)

To see a list of my commands use `/help`.

I'm not made to be used on any group, but if you want you can fork me and make modifications according to your linking. My source code can be found [here](https://mau.dev/nitanmarcel/auroraoss-bot).
"""

for module in ALL_MODULES:
    imported = importlib.import_module("bot.modules." + module)
    if hasattr(imported, "__HELP__"):
        HELPABLE += "\n" + imported.__HELP__


@CommandHandler.handler(command="start", private_lock=True)
async def start(event):
    if event.raw_text[1:] != "start help":
        me = await bot.get_me()
        user = await event.get_sender()
        await event.reply(PM_START_TEXT.format(user.first_name, me.first_name), buttons=Button.url("Help", f"http://t.me/{me.username}?start=help"))


@CommandHandler.handler(command="help", private_lock=True)
@bot.on(
    events.NewMessage(
        incoming=True, pattern=r"^/start help", func=lambda x: x.is_private))
async def help(event):
    await event.reply(HELPABLE)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(CommandHandler.register_commands())
    bot.run_until_disconnected()
