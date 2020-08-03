import aiohttp

from .. import config
from ..handlers.commandhandler import CommandHandler


async def get_status():
    async with aiohttp.ClientSession() as session:
        status = {}
        for uri in config.bot.dispenser_urls:
            async with session.get(uri) as response:
                if response.status in [200, 201]:
                    status.update({uri: True})
                else:
                    status.update({uri: False})
        return status


@CommandHandler.handler(command="status", chats=[-1001361570927])
async def dispenser_status(event):
    """Check the status of out Token Dispensers"""
    reply = await event.reply("Checking Token Dispensers status! Please wait...")
    status = await get_status()
    res = str()
    for k,v in status.items():
        res += f"`{k}: ` **{'Ok' if v else 'Down'}**\n"
    await reply.edit(res)
    await event.delete()

__HELP__ = """• __`status` - Check the status of out Token Dispenser.__"""
