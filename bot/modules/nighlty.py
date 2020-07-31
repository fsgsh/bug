import datetime
import re

import aiohttp
from bs4 import BeautifulSoup
from telethon.tl.types import DocumentAttributeFilename

from .. import bot
from ..handlers.commandhandler import CommandHandler


@CommandHandler.handler(
    command="nightly", prefixes=['!', '/', '#'],
    chats=[-1001361570927, -1001374518507])
async def get_nightly(event):
    """Fetch the latest Aurora Store Nightly"""
    reply = await event.reply("`Fetching apk file ...`")
    chat = await event.get_chat()
    if chat.id == 1361570927:
        url = "https://auroraoss.com/AuroraStore/Nightly/"
    else:
        url = "https://auroraoss.com/AuroraDroid/Nightly/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as get:
            if get.status in [200, 201]:
                soup = BeautifulSoup(await get.text(), features="html.parser")
                nightlies = {}
                for td in soup.find_all("tr"):
                    version = td.find("td", class_="fb-n")
                    date = td.find("td", class_="fb-d")
                    if version and date:
                        try:
                            nightlies.update({datetime.datetime.strptime(
                                date.text, "%Y-%m-%d %H:%M"): version.text})
                        except ValueError:
                            pass
                latest_date = sorted(nightlies.keys(), reverse=True)[0]
                latest_version = nightlies[latest_date]
                async with session.get(f"{url}{latest_version}") as apk:
                    await bot.send_file(event.chat, await apk.read(), caption=f"**Aurora Nightly uploaded at** `{latest_date.strftime('%Y-%m-%d %H:%M')}`",
                                        attributes=[DocumentAttributeFilename(file_name=latest_version)])
        await reply.delete()

__HELP__ = """\n• __`nightly` - Get the latest Aurora Nightly available. (This command can also be used as a note)__"""
