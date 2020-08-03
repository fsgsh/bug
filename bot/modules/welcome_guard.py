import asyncio
import datetime

from telethon.errors import UserNotParticipantError
from telethon.events import CallbackQuery
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin

from .. import bot, config
from ..handlers.joinhandler import JoinHandler
from ..spamwatch.cli import SpamWatchClinet
from ..utils.welcome_util import get_default_welcome


class JoinedUser:
    def __init__(self, user, chat, date):
        self.user_id = user.id
        self.chat_id = chat.id
        self.date = date
        self.is_human = asyncio.Event()

    async def wait_for_confirm(self, delay):
        await asyncio.wait_for(self.is_human.wait(), delay)

    async def confirm(self):
        self.is_human.set()


JOINED_USERS = {}


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
        if added_by is not None and added_by.id in JOINED_USERS.keys():
            joined_user = JOINED_USERS[added_by.id]
            for u in joined_user.values():
                try:
                    result = await bot(GetParticipantRequest(u.chat_id, u.user_id))
                    if not isinstance(result.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                        await bot.edit_permissions(u.chat_id, u.user_id, view_messages=False)
                        del JOINED_USERS[u.user_id][u.chat_id]
                        return await bot.send_message(u.chat_id,
                                                      f"Banning [{result.users[0].first_name}](tg://user?id={result.users[0].id})\nReason: Spam add.")
                except UserNotParticipantError:
                    pass
        else:
            return await bot.kick_participant(chat, await bot.get_me())
    else:
        user = await event.get_user()
        if user.id not in JOINED_USERS.keys():
            JOINED_USERS.update({user.id: {}})
        joined_user = JoinedUser(user, chat, datetime.datetime.now())
        JOINED_USERS[user.id].update({chat.id: joined_user})
        msg = await event.reply(get_default_welcome(chat, user),
                                buttons=[Button.inline("Click me!", "verify|" + str(user.id))])
        await bot.edit_permissions(chat, user, until_date=None, send_messages=False)
        try:
            await joined_user.wait_for_confirm(300)
            if chat.id in JOINED_USERS.keys():
                del JOINED_USERS[user.id][chat.id]
        except asyncio.TimeoutError:
            if chat.id in JOINED_USERS[user.id].keys():
                del JOINED_USERS[user.id][chat.id]
            await bot.kick_participant(chat.id, user.id)
            await event.delete()
            await msg.delete()


spamwatch = SpamWatchClinet()


@bot.on(CallbackQuery)
async def confirm_human(event):
    """When the joined user clicks this button he will be unmuted."""
    data = event.data.decode()
    if data.startswith("verify|"):
        user = await event.get_sender()
        if str(user.id) != data.split("|")[1]:
            return await event.answer("Who are you again?")
        chat = await event.get_chat()
        is_banned = await spamwatch.get_ban(user.id)
        if chat.id in JOINED_USERS[user.id]:
            wait_time = JOINED_USERS[user.id][chat.id].date + \
                datetime.timedelta(seconds=5)
            passed = wait_time - datetime.datetime.now()
            if passed.seconds <= 5:
                return await event.answer(f"Whoha, too fast. You need to wait {passed.seconds} seconds before pressing the button.")

            await JOINED_USERS[user.id][chat.id].confirm()
            del JOINED_USERS[user.id][chat.id]
            if is_banned:
                await event.edit(
                    f"""
                    [{user.first_name}](tg://user?id={user.id}) I'm afraid your account is marked as suspicious, for the groups safety you'll be able to send only text messages for the next 48 hours.
                    \n**Reason:** __{is_banned.reason}__
                    """
                )
                await bot.edit_permissions(chat, user, until_date=datetime.timedelta(hours=48),
                                           send_games=False,
                                           send_gifs=False,
                                           send_inline=False,
                                           send_media=False,
                                           send_polls=False,
                                           send_stickers=False)
            else:
                await bot.edit_permissions(chat, user, send_messages=True,
                                           send_gifs=True,
                                           send_inline=True,
                                           send_media=True,
                                           send_polls=True,
                                           send_stickers=True
                                           )
                service = await (await event.get_message()).get_reply_message()
                if service:
                    await service.delete()
                await event.delete()
