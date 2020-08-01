import datetime
import re

from telethon.errors.rpcerrorlist import UserAdminInvalidError
from telethon.events import NewMessage
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.tl.functions.channels import GetParticipantRequest
from tld import get_fld

from .. import bot

BLACKLIST = [line.rstrip('\n')
             for line in open("domains.blacklist", "r").readlines()]


@bot.on(NewMessage(func=lambda x: not x.is_private))
async def spam_guard(event):
    """Checks if the user sends any type of link, and compares it against the blacklisted domains.
        If the domain is blacklisted the user will be muted for 5 minutes
    """
    if event.entities:
        is_spam = False
        urls = []
        for ent in event.entities:
            if isinstance(ent, MessageEntityTextUrl):
                urls.append(ent.url)

            if isinstance(ent, MessageEntityUrl):
                urls.append(event.text[ent.offset:].split()[0])

        for url in urls:
            if not url.startswith(
                    "http://") and not url.startswith("https://"):
                url = "http://" + url
            if get_fld(url) in BLACKLIST:
                is_spam = True
                continue
        if is_spam:
            chat = await event.get_chat()
            user = await event.get_sender()
            result = await bot(GetParticipantRequest(chat, user))
            if isinstance(result.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
                return
            await event.delete()
            try:
                await bot.edit_permissions(chat, user, send_messages=False, until_date=datetime.timedelta(minutes=5))
                await bot.send_message(chat, f"**Restricted **[{user.first_name}](tg://user?id={user.id}) **for `5` minutes**\n\n**Reason:** __Use of restricted url!!__")
            except UserAdminInvalidError:
                pass
