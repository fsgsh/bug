import asyncio
import datetime

from telethon.errors import UserNotParticipantError
from telethon.events import CallbackQuery
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import InputChannel, InputUser, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.utils import get_display_name, get_input_peer

from .. import bot, config
from ..handlers.joinhandler import JoinHandler
from ..spamwatch.cli import SpamWatchClinet
from ..utils.welcome_util import get_default_welcome


class JoinedUser:
    def __init__(self, user, chat):
        self.id = user.id
        self.chat_id = chat.id
        self.name = get_display_name(user)
        self.is_human = asyncio.Event()

    async def wait_for_confirm(self, delay):
        await asyncio.wait_for(self.is_human.wait(), delay)

    async def confirm(self):
        self.is_human.set()


JOINED_USERS: dict = {}


@JoinHandler.handler()
async def welcome(event):
    """Mutes the user upon joining untill the "Click Me" button is pressed. If the user fails to press the button in withing 5 minutes
        the respective user will be kicked.
       This also checks if the joined user tries to add the bot to a group before confirming he's human.
       Adds a little protection against spammers but the only downside is that it won't detect if it's added to a channel since spammers can't add a bot to a channel without giving him admin access"""
    global JOINED_USERS
    chat = await event.get_chat()
    if chat.id not in config.bot.allowed_chats:
        added_by = await event.get_added_by()
        if added_by is not None:
            if added_by.id in JOINED_USERS.keys():
                user = JOINED_USERS[added_by.id]
                try:
                    result = await bot(GetParticipantRequest(user.chat_id, user.id))
                    if not isinstance(result.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                        await bot.edit_permissions(user.chat_id, user.id, view_messages=False)
                        return await bot.send_message(user.chat_id,
                                                      f"Banning [{result.users[0].first_name}](tg://user?id={result.users[0].id})\nReason: Spam add.")
                except UserNotParticipantError:
                    await bot.edit_permissions(user.chat_id, user.id, view_messages=False)
            else:
                return await bot.kick_participant(chat, await bot.get_me())
        else:
            return await bot.kick_participant(chat, await bot.get_me())
    else:
        user = await event.get_user()
        if user.id not in JOINED_USERS.keys():
            joined_user = JoinedUser(user, chat)
            JOINED_USERS.update({joined_user.id: joined_user})

        msg = await event.reply(get_default_welcome(chat, user),
                                buttons=[Button.inline("Click me!", "confirmhuman")])
        try:
            await bot.edit_permissions(chat, user, until_date=None, send_messages=False)
            await joined_user.wait_for_confirm(60 * 5)
        except asyncio.TimeoutError:
            await bot.kick_participant(chat.id, user.id)
            await event.delete()
            await msg.delete()



spamwatch = SpamWatchClinet()


@bot.on(CallbackQuery)
async def confirm_human(event):
    """When the joined user clicks this button he will be unmuted."""
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
