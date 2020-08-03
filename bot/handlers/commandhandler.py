import inspect
import os
import re
import sys
from datetime import datetime
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
                __lgw_marker_local__ = 0
                if private_lock and not event.is_private:
                    me = await bot.get_me()
                    return await event.reply(f"Contact me in PM for {command.title()} !",
                                             buttons=[Button.url(command.title(), f"http://t.me/{me.username}?start={command}")])
                try:
                    await f(event)
                    if len(event.next.split()) <= 1:
                        await event.delete()
                except Exception as e:
                    exc_time = datetime.now().strftime("%m_%d_%H:%M:%S")
                    file_name = f"{exc_time}_{type(e).__name__}_{f.__name__}"
                    if not os.path.exists('logs/'):
                        os.mkdir('logs/')
                    with open(f"logs/{file_name}.log", "a") as log_file:
                        log_file.write(
                            f"Exception thrown, {type(e)}: {str(e)}\n")
                        frames = inspect.getinnerframes(sys.exc_info()[2])
                        for frame_info in reversed(frames):
                            f_locals = frame_info[0].f_locals
                            if "__lgw_marker_local__" in f_locals:
                                continue

                            log_file.write(f"File{frame_info[1]},"
                                           f"line {frame_info[2]}"
                                           f" in {frame_info[3]}\n"
                                           f"{frame_info[4][0]}\n")

                            for k, v in f_locals.items():
                                log_to_str = str(v).replace("\n", "\\n")
                                log_file.write(f"    {k} = {log_to_str}\n")
                        log_file.write("\n")

                    raise
        return warper

    @staticmethod
    async def register_commands():
        await bot(SetBotCommandsRequest(__COMMANDS__))
