import importlib
import random
import time
import re

from sys import argv
from typing import Optional
import RocksAlexaRobot.modules.sql.users_sql as sql
from RocksAlexaRobot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,UPDATES_CHANNEL,
    dispatcher,
    StartTime,
    telethn,
    updater)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from RocksAlexaRobot.modules import ALL_MODULES
from RocksAlexaRobot.modules.helper_funcs.chat_status import is_user_admin
from RocksAlexaRobot.modules.helper_funcs.misc import paginate_modules
from RocksAlexaRobot.modules.disable import DisableAbleCommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, __version__ as ptbver
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown



def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time



PM_START_TEXT = """
 ──『[ᴀʟᴇxᴀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ](https://telegra.ph/file/a39d85b972b38e2d5fd91.jpg)』

*ʜᴇʟʟᴏ {} !*
✪ ɪ ᴀᴍ ᴀʟᴇxᴀ sᴜᴘᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴡɪᴛʜ ᴜsᴇғᴜʟʟ ғᴇᴀᴛᴜʀᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛʜᴇɴ sᴇᴇ ᴍʏ ᴘᴏᴡᴇʀs ʙᴜᴅᴅʏ 😔
────────────────────────
× *Uptime:* `{}`
× `{}` *users, across* `{}` *chats.*
────────────────────────
✪ ʜɪᴛ /help ᴛᴏ sᴇᴇ ᴍʏ ᴘᴏᴡᴇʀ ʙᴜᴅᴅʏ ✌️.
────────────────────────
✪ [CHANNEL](t.me/AsadSupport) - [SUPPORT](t.me/Shayri_Music_Lovers)
────────────────────────
✪ ──『*ᴛʜᴀɴᴋs  ғᴏʀ  ᴜsɪɴɢ*』
"""
PMSTART_CHAT = (
    "[ Get Busy Living Or Get Busy Dying!!!](https://telegra.ph/file/f821830759461370f68d9.jpg)",
    "[I'm Dr Asad Ali Project](https://telegra.ph/file/85e4f39239fd84a27d138.jpg)",
    "[Turn Your Wounds Into Wisdom 🔥](https://telegra.ph/file/35e730dea457c85cc367b.mp4)",
    "[Hahahahaha I'm Alexa!!!!](https://telegra.ph/file/6f43301a3e43d20f7906a.jpg)", )

buttons = [
    [
        InlineKeyboardButton(
                            text="💖 ᴀᴅᴅ ᴀʟᴇxᴀ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 💖",
                            url="t.me/ALEXA_MANAGEMENTBOT?startgroup=true"),
                    ],
                   [
                       InlineKeyboardButton(text="💌 ᴋɪɴɢ", url="t.me/HarshitSharma361"),
                       InlineKeyboardButton(text="💌 ғᴇᴅ", url="t.me/Part_Of_Rocks"),
                     ],
                    [                  
                       InlineKeyboardButton(
                             text="💌 ᴏᴡɴᴇʀ",
                             url=f"https://t.me/Dr_Assad_Ali"),
                       InlineKeyboardButton(
                             text="💌 ɴᴇᴛᴡᴏʀᴋ",
                             url=f"https://t.me/Shayri_Music_Lovers"),
                        ],
                       [
                           InlineKeyboardButton(text="💓 ʟᴏᴠᴇ", url="t.me/Give_Me_Heart"
         ),
    ],
]

HELP_STRINGS = """
Hey there, I'm *Rocks Alexa*!
To make me functional, make sure that i have enough rights in your group.
Helpful commands:
- /start: Starts me! You've probably already used this.
- /help: Sends this message; I'll tell you more about myself!
- /donate: Gives you info on how to support me and my creator.
If you want to report bugs or have any questions on how to use me then feel free to reach out: @AsadSupport.
All commands can be used with the following: [(/),(!),(?),(.),(~)](https://telegra.ph/file/9d22fedee29fdefdb4862.jpg)
List of all the Modules:
""".format(
    dispatcher.bot.first_name,
    "" if not ALLOW_EXCL else "📝All commands can either be used with / or !.",
)

HELP_MSG = "Click the button below to get help manu in your pm."
DONATE_STRING = """Contact to My Pretty [OWNER](t.me/Dr_Asad_Ali)"""
HELP_IMG= "https://telegra.ph/file/93aa52512ccd256888b28.jpg"
GROUPSTART_IMG= "https://telegra.ph/file/35e730dea457c85cc367b.mp4"

PM_IMG = ( "https://telegra.ph/file/8d2bf852a53bd13fb8037.jpg",
           "https://telegra.ph/file/6f43301a3e43d20f7906a.jpg",
           "https://telegra.ph/file/c71c9940f27143f1d6b7b.jpg",
           "https://telegra.ph/file/93aa52512ccd256888b28.jpg",
           "https://telegra.ph/file/0d7fd638c3c2ea21176a1.jpg", )


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("RocksAlexaRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)



def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅Back", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_message.reply_text(
                random.choice(PMSTART_CHAT),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
            first_name = update.effective_user.first_name
            update.effective_message.reply_photo(
               random.choice(PM_IMG),PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        first_name = update.effective_user.first_name
        update.effective_message.reply_video(
            GROUPSTART_IMG, caption= "*hey {},*\n*Official Rocks Alexa here*\n*Power lavel time* : {} ".format(
             first_name,uptime
            ),
            parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
                [
                  [
                  InlineKeyboardButton(text="💌 ᴋɪɴɢ ", url=f"t.me/Dr_Assad_Ali"),
                  InlineKeyboardButton(text="😎 ᴜᴘᴅᴀᴛᴇs ", url=f"t.me/AsadSupport"),
                  ]
                ]
            ),
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors



def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Powered by [Dr Asad Ali](t.me/Dr_Assad_Ali) And [Harshit Sharma](t.me/HarshitSharma361)\nHere is the help for the *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="⬅ Back", callback_data="help_back"),
                      InlineKeyboardButton(text="⬅ Home", callback_data="alexa_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass



def alexa_data_callback(update, context):
    query = update.callback_query
    if query.data == "alexa_":
        query.message.edit_text(
            text="""CallBackQueriesData Here""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="alexa_back")
                 ]
                ]
            ),
        )
    elif query.data == "alexa_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )




def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_photo(
            HELP_IMG, HELP_MSG,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )



def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))



def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)



def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 5303133436 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop




def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}","[乛𝙍𝙊𝘾𝙆𝙎🕊️⃝🦋⁪⁬𝘼𝙇𝙀𝙓𝘼🕊️⃝🦋𝙄𝙎🕊️⃝🦋𝘽𝘼𝘾𝙆](https://telegra.ph/file/52b14a4c35f8ebb2b7bf1.jpg)", parse_mode=ParseMode.MARKDOWN) 
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!",
            )
        except BadRequest as e:
            LOGGER.warning(e.message)


    start_handler = DisableAbleCommandHandler("start", start)

    help_handler = DisableAbleCommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    data_callback_handler = CallbackQueryHandler(alexa_data_callback, pattern=r"alexa_")
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(data_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Rocks Alexa is now alive and functioning")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    main()
