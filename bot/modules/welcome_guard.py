import asyncio
import datetime

from telethon.events import CallbackQuery
from telethon.tl.custom import Button
from telethon.tl.types import InputChannel, InputUser
from telethon.utils import get_display_name, get_input_peer

from .. import bot, config
from ..handlers.joinhandler import JoinHandler
from ..spamwatch.cli import SpamWatchClinet
from ..utils.welcome_util import get_default_welcome


class JoinedUser:
    def __init__(self, user):
        self.id = user.id
        self.name = get_display_name(user)
        self.is_human = asyncio.Event()

    async def wait_for_confirm(self, delay):
        await asyncio.wait_for(self.is_human.wait(), delay)

    async def confirm(self):
        self.is_human.set()


JOINED_USERS: dict = {}


@JoinHandler.handler()
async def welcome(event):
    global JOINED_USERS
    chat = await event.get_chat()
    user = await event.get_user()
    me = await bot.get_me()
    if chat.id not in config.bot.allowed_chats:
        return await bot.kick_participant(chat, me)
    if user.id not in JOINED_USERS.keys():
        joined_user = JoinedUser(user)
        JOINED_USERS.update({joined_user.id: joined_user})
    await bot.edit_permissions(chat, user, until_date=None, send_messages=False)
    msg = await event.reply(get_default_welcome(chat, user),
                      buttons=[Button.inline("Click me!", "confirmhuman")])
    try:
        await joined_user.wait_for_confirm(60 * 5)
    except asyncio.TimeoutError:
        await bot.kick_participant(chat.id, user.id)
        await event.delete()
        msg.delete()




spamwatch = SpamWatchClinet()


@bot.on(CallbackQuery)
async def confirm_human(event):
    data = event.data.decode()
    if data == "confirmhuman":
        clicked = await event.get_sender()
        if clicked.id not in JOINED_USERS.keys():
            return await event.answer("Who are you again?")
        chat = await event.get_chat()
        is_banned = await spamwatch.get_ban(clicked.id)
        await event.answer("Confirmed")
        if is_banned:
            await event.edit(
                f"""
                [{clicked.first_name}](tg://user?id={clicked.id}) I'm afraid your account is marked as suspicious, for the groups safety you'll be able to send only text messages for the next 48 hours.
                \n**Reason:** __{is_banned.reason}__
                """
            )
            await bot.edit_permissions(chat, clicked, until_date=datetime.timedelta(hours=48),
                                       send_games=False,
                                       send_gifs=False,
                                       send_inline=False,
                                       send_media=False,
                                       send_polls=False,
                                       send_stickers=False)
        else:
            await event.delete()
            await bot.edit_permissions(chat, clicked, until_date=None, send_messages=True)
        await JOINED_USERS[clicked.id].confirm()
        del JOINED_USERS[clicked.id]
