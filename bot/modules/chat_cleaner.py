import asyncio
from .. import bot, config, LOGGER
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.errors.rpcerrorlist import UserAdminInvalidError

DELAY = 24 * 60 * 60

async def clear_deleted():
    """Clears all the deleted accounts from the chat"""
    while True:
        for chat in config.bot.allowed_chats:
            async for user in bot.iter_participants(chat):
                if user.deleted:
                    if user.deleted:
                        if not isinstance(user.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                            try:
                                await bot.kick_participant(chat, user)
                            except UserAdminInvalidError:
                                pass
        await asyncio.sleep(DELAY)


bot.loop.create_task(clear_deleted())


