import datetime
import re

from telethon.events import CallbackQuery
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.types import (ChannelParticipantAdmin,
                               ChannelParticipantCreator,
                               MessageMediaWebPage,
                               MessageMediaUnsupported)

from .. import bot, config
from ..handlers.commandhandler import CommandHandler


@CommandHandler.handler(command="suggestion", chats=config.bot.allowed_chats)
async def add_suggestion(event):
    """Users can use this to make suggestions related to the Aurora Apps. Their suggestion will be sent to a channel if approved."""
    if not event.is_reply and not event.file and len(event.text.split()) == 1:
        return await event.delete()
    msg = event.message
    if event.is_reply:
        msg = await event.get_reply_message()
    await msg.reply("Thanks for your suggestion. The admins of this group will review it and approve it if needed!",
                    buttons=[Button.inline("Approve", "appsug"), Button.inline("Reject", "ignoresug")])


@CommandHandler.handler(command="bug", chats=config.bot.allowed_chats)
async def add_bug(event):
    """Users can use this to report bugs related to the Aurora Apps. Their report will be sent to a channel if approved."""
    if not event.is_reply and not event.file and len(event.text.split()) == 1:
        return await event.delete()
    msg = event.message
    if event.is_reply:
        msg = await event.get_reply_message()
    await msg.reply("Thanks for your bug report. The admins of this group will review it and approve it if needed!",
                    buttons=[Button.inline("Approve", "appbug"), Button.inline("Reject", "ignorebug")])


@bot.on(CallbackQuery)
async def review(event):
    """Buttons for admins to approve or reject a bug/suggestion"""
    if event.data.decode() not in [
            "appsug", "appbug", "ignoresug", "ignorebug", "mark"]:
        return
    sender = await event.get_sender()
    try:
        participant = await bot(GetParticipantRequest(event.chat_id, sender.id))
    except UserNotParticipantError:
        return await event.answer()
    if not isinstance(
            participant.participant,
            (ChannelParticipantAdmin, ChannelParticipantCreator)):
        return await event.answer()
    if event.data.decode() == "mark":
        msg = await event.get_message()
        return await msg.edit(re.sub(r"Pending \.\.\.$", "Solved", msg.text), buttons=None)
    by_admin = "[{}](tg://user?id={})".format(sender.first_name, sender.id)
    at_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    if event.data.decode() == 'ignoresug':
        return await event.edit("Your suggestion has been rejected by {} at `{}`!".format(by_admin, at_time))
    if event.data.decode() == 'ignorebug':
        return await event.edit("Your bug report has been rejected by {} at `{}`!".format(by_admin, at_time))
    rep_msg = await(await event.get_message()).get_reply_message()
    by_user = "[{}](tg://user?id={})".format(rep_msg.sender.first_name,
                                             rep_msg.sender.id)
    in_chat = "[{}](https://t.me/{})".format(rep_msg.chat.title,
                                             rep_msg.chat.username)
    file = rep_msg.media or rep_msg.document
    if isinstance(file, (MessageMediaWebPage, MessageMediaUnsupported)):
        file = None
    text = rep_msg.text
    is_suggestion = event.data.decode() == "appsug"
    if text:
        text = re.sub(r"^.suggestion", "", re.sub(r"^.bug", "", text))
    approved_format = "{} from {} in {} \n\n{} \n\nApproved by {} at `{}`\nStatus: Pending ...".format(
        "Suggestion" if is_suggestion else "Bug", by_user, in_chat, text, by_admin, at_time)

    await bot.send_message(config.bot.suggesion_chat, message=approved_format, file=file,
                           buttons=[Button.inline("Mark As Solved!", "mark")])
    if is_suggestion:
        await event.edit(
            "Your suggestion has been forwarded to our channel by {} at `{}`! Thanks!".format(by_admin, at_time))
    else:
        await event.edit(
            "Your bug report has been forwarded to our channel by {} at `{}`! Thanks!".format(by_admin, at_time))

__HELP__ = """• __`suggestion` <suggestion> - Sends us a suggestion for our apps (Works as reply too)__
            \n• __`bug` <bug> - Report a bug you've found in our apps (Works as reply too)__"""
