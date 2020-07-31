from telethon.events import ChatAction

from .. import bot


class JoinHandler:
    @staticmethod
    def handler():
        def warper(f):
            @bot.on(ChatAction)  # return custom result?
            async def execute(event):
                if event.user_joined or event.user_added:
                    await f(event)
        return warper
