import html

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from FallenRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
)
from FallenRobot.modules.helper_funcs.extraction import extract_user_and_text
from FallenRobot.modules.helper_funcs.string_handling import extract_time
from FallenRobot.modules.log_channel import gloggable, loggable

# GIF URLs for animations
BAN_GIFS = [
    "https://files.catbox.moe/hknv78.mp4",
]

KICK_GIFS = [
    "https://files.catbox.moe/3kriz2.mp4",
]

MUTE_GIFS = [
    "https://files.catbox.moe/w1rpq0.mp4",
]


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("Can't seem to find this person.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Oh yeah, ban myself, noob!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text(
                "chal be ya mera owner mere bus ki na hai isko ban karna tu khud dekh le 😔"
            )
        elif user_id in DEV_USERS:
            message.reply_text("I can't act against our own.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Fighting this Dragon here will put civilian lives at risk."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Bring an order from Heroes association to fight a Demon disaster."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Bring an order from Heroes association to fight a Tiger disaster."
            )
        elif user_id in WOLVES:
            message.reply_text("Wolf abilities make them ban immune!")
        else:
            message.reply_text("This user has immunity and cannot be banned.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}ʙᴀɴɴᴇᴅ\n"
        f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # Sending animation with inline keyboard for unban
        keyboard = [
            [InlineKeyboardButton("𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥", url=f"tg://user?id={member.user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_animation(
            chat.id,
            BAN_GIFS[0],
            caption=log,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            message.reply_text("ʙᴀɴɴᴇᴅ !", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm...that didn't work...")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I don't feel like it.")
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "ᴛᴇᴍᴩ ʙᴀɴ\n"
        f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>ᴛɪᴍᴇ:</b> {time_val}"
    )
    if reason:
        log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

    try:
        chat.ban_member(user_id, until_date=bantime)

        # Sending animation with inline keyboard for unban
        keyboard = [
            [InlineKeyboardButton("𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥", url=f"tg://user?id={member.user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_animation(
            chat.id,
            BAN_GIFS[0],
            caption=log,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                f"Banned! User will be banned for {time_val}.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't ban that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("I'm not going to kick myself!")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I can't kick this user.")
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "🦵 ᴋɪᴄᴋᴇᴅ\n"
        f"<b>ᴋɪᴄᴋᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)

        # Sending animation with inline keyboard for unban
        keyboard = [
            [InlineKeyboardButton("𝗞𝗜𝗖𝗞𝗘𝗗 𝗨𝗦𝗘𝗥", url=f"tg://user?id={member.user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_animation(
            chat.id,
            KICK_GIFS[0],
            caption=log,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            message.reply_text("User kicked!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR kicking user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("I couldn't kick that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def mute(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("I'm not going to mute myself!")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I can't mute this user.")
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to mute this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    mute_time = extract_time(message, time_val)

    if not mute_time:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "🔇 ᴍᴜᴛᴇᴅ\n"
        f"<b>ᴍᴜᴛᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>ᴛɪᴍᴇ:</b> {time_val}"
    )
    if reason:
        log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

    try:
        chat.restrict_member(
            user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            ),
            until_date=mute_time,
        )

        # Sending animation with inline keyboard for unban
        keyboard = [
            [InlineKeyboardButton("𝗠𝗨𝗧𝗘 𝗨𝗦𝗘𝗥", url=f"tg://user?id={member.user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_animation(
            chat.id,
            MUTE_GIFS[0],
            caption=log,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            message.reply_text(
                f"User muted! User will be muted for {time_val}.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR muting user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("I couldn't mute that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("How would I unban myself if I wasn't here?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Isn't this person already here?")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Yep, this user can join again!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"🆗 ᴜɴʙᴀɴɴᴇᴅ\n"
        f"<b>ᴜɴʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS and user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except ValueError:
        message.reply_text("Give a valid chat ID.")
        return

    chat = bot.get_chat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Aren't you already in the chat?")
        return

    chat.unban_member(user.id)
    message.reply_text("Yep, I have unbanned you.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"🆗 ᴜɴʙᴀɴɴᴇᴅ\n"
        f"<b>ᴜɴʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log


@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("I wish I could... but you're an admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*kicks you out of the group*")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@connection_status
@bot_admin
@user_admin
def dban(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if message.reply_to_message:
        replied_message = message.reply_to_message
        user_id = replied_message.from_user.id
        reason = " ".join(context.args) if context.args else ""

        if not user_id:
            message.reply_text("No user found in the replied message.")
            return ""

        member = chat.get_member(user_id)

        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#{'S' if False else ''}ʙᴀɴɴᴇᴅ\n"
            f"<b>ʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"

        try:
            # Ban the user
            chat.ban_member(user_id)

            # Delete the replied message
            try:
                bot.delete_message(chat.id, replied_message.message_id)
            except BadRequest as excp:
                LOGGER.warning(update)
                LOGGER.exception(
                    "ERROR deleting replied message %s in chat %s (%s) due to %s",
                    replied_message.message_id,
                    chat.title,
                    chat.id,
                    excp.message,
                )

            # Delete the command message
            try:
                bot.delete_message(chat.id, message.message_id)
            except BadRequest as excp:
                LOGGER.warning(update)
                LOGGER.exception(
                    "ERROR deleting command message %s in chat %s (%s) due to %s",
                    message.message_id,
                    chat.title,
                    chat.id,
                    excp.message,
                )
                return "User banned, but failed to delete the command message."

            # Sending animation with inline keyboard for unban
            keyboard = [
                [
                    InlineKeyboardButton(
                        "𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥", url=f"tg://user?id={member.user.id}"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_animation(
                chat.id,
                BAN_GIFS[0],
                caption=log,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )
            return log

        except BadRequest as excp:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Unable to ban the user.")
            return ""

    else:
        message.reply_text("You need to reply to a message to use this command.")
        return ""


__help__ = """
 ❍ /kickme*:* kicks the user who issued the command

*Admins only:*
 ❍ /ban <userhandle>*:* bans a user. (via handle, or reply)
 ❍ /sban <userhandle>*:* Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply)
 ❍ /tban <userhandle> x(m/h/d)*:* bans a user for `x` time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
 ❍ /unban <userhandle>*:* unbans a user. (via handle, or reply)
 ❍ /kick <userhandle>*:* kicks a user out of the group, (via handle, or reply)
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
KICK_HANDLER = CommandHandler("kick", kick)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=Filters.chat_type.groups
)
MUTE_HANDLER = CommandHandler("tmute", mute)

# Add the handler for the new command
DBAN_HANDLER = CommandHandler("dban", dban)
dispatcher.add_handler(DBAN_HANDLER)
dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(MUTE_HANDLER)

__mod_name__ = "Bans"
