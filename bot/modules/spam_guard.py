import datetime
import re

from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserNotParticipantError
from tld.exceptions import TldDomainNotFound
from telethon.events import NewMessage
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.tl.functions.channels import GetParticipantRequest
from tld import get_fld

from .. import bot

DOMAIN_BLACKLIST = [line.rstrip('\n').lower()
             for line in open("domains.blacklist", "r").readlines()]

URL_BLACKLIST = [re.sub(r"^http(\w?)://", "", line.rstrip('\n').lower())
             for line in open("urls.blacklist", "r").readlines()]



def check_url(url):
    if re.sub(r"^http(\w?)://", "", url.lower()) in URL_BLACKLIST:
        return True
    if not re.search(r"^http(\w?)://", url):
        url = re.sub("^", "http://", url)
        try:
            if get_fld(url) in DOMAIN_BLACKLIST:
                return True
        except TldDomainNotFound:
            return True

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
            is_spam = check_url(url)
            if is_spam:
                chat = await event.get_chat()
                user = await event.get_sender()
                try:
                    result = await bot(GetParticipantRequest(chat, user))
                except UserNotParticipantError:
                    await bot.edit_permissions(chat, user, view_messages=False)
                    await bot.send_message(chat,
                                           f"**Banned:** [{user.first_name}](tg://user?id={user.id})\n\n**Reason:** __Spam!!__")
                    return
                if isinstance(result.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
                    return
                await event.delete()
                try:
                    await bot.edit_permissions(chat, user, send_messages=False,
                                               until_date=datetime.timedelta(minutes=5))
                    await bot.send_message(chat,
                                           f"**Restricted **[{user.first_name}](tg://user?id={user.id}) **for `5` minutes**\n\n**Reason:** __Use of restricted url!!__")
                except UserAdminInvalidError:
                    pass
                continue
