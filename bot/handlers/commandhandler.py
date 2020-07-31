import re
from typing import Callable, List

from telethon.events import NewMessage
from telethon.tl.custom import Button
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import BotCommand

from .. import bot

__COMMANDS__: List[BotCommand] = [BotCommand("start", "Starts this bot/Displays start message!"),
                                  BotCommand("help", "Displays bot help/bot commands")]


class CommandHandler:
    @staticmethod
    def handler(command: str, prefixes: List[str] = ["!", "/"], private_lock: bool = False, func: Callable = None,
                **kwargs):
        def warper(f: Callable):
            global __COMMANDS__
            if len(prefixes) == 1:
                _prefixes = prefixes[0]
            else:
                _prefixes = str()
                for p in prefixes:
                    _prefixes += re.escape(p) + "|"
                _prefixes = re.sub(re.escape("|") + "$", "", _prefixes)
            _pattern = r"^({}){}\b".format(_prefixes, command)
            if f.__doc__:
                __COMMANDS__.append(BotCommand(command, f.__doc__))

            @bot.on(NewMessage(
                pattern=_pattern,
                incoming=True,
                outgoing=False,
                func=func,
                **kwargs
            ))
            async def execute(event):
                if private_lock and not event.is_private:
                    me = await bot.get_me()
                    return await event.reply(f"Contact me in PM for {command.title()} !",
                                             buttons=[Button.url(command.title(), f"http://t.me/{me.username}?start={command}")])
                await f(event)
        return warper

    @staticmethod
    async def register_commands():
        await bot(SetBotCommandsRequest(__COMMANDS__))
