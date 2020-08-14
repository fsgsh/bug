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


TELEGRAM_DOMAINS = ['t.me',
                    'telegram.org',
                    'telegram.dog',
                    'telegra.ph',
                    'tdesktop.com',
                    'telesco.pe',
                    'graph.org',
                    'contest.dev']

def _get_fld(uri):
    if not re.search(r"^http(\w?)://", uri):
        uri = re.sub("^", "http://", uri)
    try:
        return get_fld(uri)
    except TldDomainNotFound:
        return None

def check_url(url):
    if re.sub(r"^http(\w?)://", "", url.lower()) in URL_BLACKLIST:
        return True
    fdl = _get_fld(url)
    if not fdl:
        return True
    elif fdl in DOMAIN_BLACKLIST:
        return True

@bot.on(NewMessage(func=lambda e: not e.is_private))
async def spam_guard(event):
    """Checks if the user sends any type of link, and compares it against the blacklisted domains.
        If the domain is blacklisted the user will be muted for 5 minutes
    """
    FORMAT = "**Banned: [{first_name}](tg://user?id={user_id})\n\n**Reason:** __Spam!!__"
    if event.entities:
        for ent in event.entities:
            url = str()
            if isinstance(ent, MessageEntityTextUrl):
                url = ent.url
            if isinstance(ent, MessageEntityUrl):
                url = event.text[ent.offset:].split()[0]
            if not bool(url):
                return
            chat = await event.get_chat()
            user = await event.get_sender()
            check = check_url(url)
            fld = _get_fld(url)
            if check or fld not in TELEGRAM_DOMAINS:
                try:
                    result = await bot(GetParticipantRequest(chat, user))
                    if not isinstance(result.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
                        if check:
                            await event.delete()
                            await bot.edit_permissions(chat, user, view_messages=False)
                            await bot.send_message(chat, FORMAT.format(first_name=user.first_name, user_id=user.id))
                        elif chat.id in [1374518507, 1195021050, 1361570927]:
                            await event.delete()
                            await bot.send_message(chat,
                                                     f"**Deleted message from:** [{user.first_name}](tg://user?id={user.id})\n__External links are not allowed in this chat! Please move to__ [OffTopic Chat](https://t.me/AuroraOT)",
                                                   link_preview=False)

                except UserNotParticipantError:
                    await bot.edit_permissions(chat, user, view_messages=False)
                    await bot.send_message(chat, FORMAT.format(first_name=user.first_name, user_id=user.id))