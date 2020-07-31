import aiohttp

from .. import config
from ..handlers.commandhandler import CommandHandler


async def get_status():
    async with aiohttp.ClientSession() as session:
        async with session.get(config.bot.dispenser_url) as response:
            if response.status in [200, 201]:
                return True


@CommandHandler.handler(command="status", chats=[-1001361570927])
async def dispenser_status(event):
    """Check the status of out Token Dispenser"""
    reply = await event.reply("Checking Token Dispenser status! Please wait...")
    try:
        status = await get_status()
    except Exception:
        status = False

    if not status:
        return await reply.edit("Our Token Dispenser is currently down. Please use alternatives or wait until the issue is resolved. Thanks!")

    await reply.edit("Our Token Dispenser is up and running. If you can't login into AuroraStore anonymously please check if you have an internet connection, force close the app or wait for an administrator to reply to you. Thanks!")


__HELP__ = """• __`status` - Check the status of out Token Dispenser.__"""
