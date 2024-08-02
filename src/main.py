# imports
from PIL import Image, ImageDraw, ImageFont
import os
import hikari.errors
import requests
import hikari
import lightbulb
from lightbulb.ext import tasks
import logging
import random
import string
from datetime import datetime
import platform
import sys
import json
from textwrap import TextWrapper as tw
import atexit
import time
import imagetext_py as imgtxt
import math
import miru
import asyncio
import dotenv

# some old regex. this was to remove @/# mentions in messages
MENTION_DETECT = r"<.\d*>"

# platform.
uname = platform.uname()

# create a class for a custom exception
class IncorrectPlatformError(Exception):
    pass

# not windows error.
# ===[DO NOT REMOVE!!]===
# if you remove, the bot will FAIL to work with a 100% failure rate.
# to supress the warning, just remove the logging line!
if f"{uname.system}" != "Windows":
    #raise IncorrectPlatformError("This script was built for Windows! To supress this exception, comment it out.")
    notWindows = True
else:
    notWindows = False

#def exitFunc():
#    breakpoint()
#
#atexit.register(exitFunc)

# init constants, these are self explanitory
USER_PAIR_OFFSET = 128
QUOTE_SIZE = 96
USER_DEETZ_SIZE = 64
QUOTE_PXLS = 900

dotenv.load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]

# create the bot application
bot = lightbulb.BotApp(BOT_TOKEN, allow_color=False)

# DataStore variables
bot.d.activityCycleRunning = True
bot.d.activityCycle = []
bot.d.INSTANCE_START_TIME = math.floor(time.time())
bot.d.BUILD = "v2024.0802.1"
bot.d.last_module_reboot = math.floor(time.time())

miru.install(bot)
imgtxt.FontDB.SetDefaultEmojiOptions(imgtxt.EmojiOptions(parse_discord_emojis=True))
imgtxt.FontDB.LoadFromDir("./defaultAssets/fonts")

# the messages that get displayed when an error occurs
cooldownList = ["HEY!", "Wait up!", ">:C", "a.", ":ice_cube:", ":fire: :fire: :fire:", "Cooldown'd", "Fun remover", ":)", ":nerd: :nerd: :nerd:"]
permissionErrorFlavourText = ["nope.", "I don't think I can do that...", ":nerd:", ":warning:", "oi", "The law requires I answer no.", "`permissionError`", "nuh uh."]
errorFlavourText = ["i didn't touch nothing!", "deleting system 32...", "umm uhh", "im so silly!", "oops...", "i think i dropped something.", "[500] internal server error"]

class bugReportView(miru.View):
    pass

# error handler
@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        errorEmbedData = {}

        if event.context.author.avatar_url:
            aviUrl = str(event.context.author.avatar_url)
        else:
            aviUrl = "https://cdn.discordapp.com/embed/avatars/0.png"

        errorEmbedData["embeds"] = [
            {
                "description": f"`{type(event.exception.original)}` -> {event.exception.original}",
                "title": "quoter broke (again).",
                "color": 0xED4245,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "footer": {
                    "text": f"{event.context.author.global_name} // @{event.context.author.username}",
                    "icon_url": aviUrl
                },
                "fields": [
                    {
                        "name": "command information",
                        "inline": True,
                        "value": f"{event.context.command.name=}"
                    },
                    {
                        "name": "interaction information",
                        "inline": True,
                        "value": f"{event.context.interaction.command_name=}\n\n{event.context.interaction.command_type=}"
                    },
                    {
                        "name": "user information",
                        "inline": True,
                        "value": f"{event.context.author.username=}\n{event.context.author.id=}"
                    }
                ]
            }
        ]

        requests.post(os.environ["ERROR_WEBHOOK"], json=errorEmbedData)
        # await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`.")

        view = bugReportView()
        view.add_item(miru.Button(label="Send bug report", style=hikari.ButtonStyle.LINK, url="https://github.com/paradoxical-autumn/quoter/issues"))

        instance_found = False

        # WHY CAN I NOT USE A DICTIONARY OF ERRORS AND SEND IT BASED OFF OF THAT?

        if isinstance(event.exception.original, hikari.errors.ForbiddenError):
            instance_found = True
            try:
                await event.context.respond(hikari.Embed(title="[403] Forbidden", description=f"I was not allowed to execute that request due to a 403 error. This is usually a sign of the bot being:\n- Incorrectly configured in the server\n- Caught by automod\n\nFor more information, contact the server admins, maybe ask them something like \"Hey, Quoter isn't working here, has it been caught by automod or does it lack the permission to upload files?\"\n\nIf this is not a problem with the server setup, please file a bug report", color=0xED4245), components=view)
            except:
                # I know wildcard except clauses are bad but shh.
                try:
                    await event.context.user.send("# Sorry!\nIt looks like you recently tried to use a command which was 403'd. This is usually a sign of the bot being:\n- Incorrectly configured in the server\n- Caught by automod\n\nFor more information, contact the server admins, maybe ask them something like \"Hey, Quoter isn't working here, has it been caught by automod or does it lack the permission to upload files?\"\n\nIf this is not a problem with the server setup, please file a bug report at <https://github.com/paradoxical-autumn/quoter/issues>")
                except hikari.errors.ForbiddenError:
                    # if user does not allow DMs.
                    pass
        
        if isinstance(event.exception.original, hikari.errors.UnauthorizedError):
            instance_found = True
            try:
                await event.context.respond(hikari.Embed(title="[401] Unauthorized", description=f"An authorization error occurred. Please try again.", color=0xED4245), components=view)
            except:
                try:
                    await event.context.user.send("# Sorry!\nIt looks like you recently tried to use a command which was 401'd. Maybe try again? If it is still being 401'd, consider filing a bug report at <https://github.com/paradoxical-autumn/quoter/issues>")
                except hikari.errors.ForbiddenError:
                    pass
        
        if isinstance(event.exception.original, hikari.errors.NotFoundError):
            instance_found = True
            try:
                await event.context.respond(hikari.Embed(title="[404] Not found", description=f"I was unable to reach a key resource. Maybe try again?", color=0xED4245), components=view)
            except:
                try:
                    await event.context.user.send("# Sorry!\nIt looks like you recently tried to use a command which was 404'd. Maybe try again? If it is still being 404'd, consider filing a bug report at <https://github.com/paradoxical-autumn/quoter/issues>")
                except hikari.errors.ForbiddenError:
                    pass
        
        if not instance_found:
            await event.context.respond(hikari.Embed(title=random.choice(errorFlavourText), description=f"An unknown error occurred.", color=0xED4245), components=view)

        logging.fatal(f"{event.exception.original}")

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond(hikari.Embed(title=random.choice(permissionErrorFlavourText), description=":no_entry_sign: You don't have authorisation to run that command!", color=0xFEE75C))

    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(hikari.Embed(title=random.choice(cooldownList), description=f"Retry after `{exception.retry_after:.2f}` seconds.", color=0x5865F2))

    elif ...:
        ...
    else:
        raise exception

#input("Suspended.")

# init cooldowns
quoteCooldownBucket = lightbulb.buckets.UserBucket
globalCooldownBucket = lightbulb.buckets.UserBucket

with open("cfgs/ranks.json", "r") as fp:
    ranks = json.load(fp)

ACTIVITY_ENUMS = {
    "watch": hikari.ActivityType.WATCHING,
    "watching": hikari.ActivityType.WATCHING,
    "listen": hikari.ActivityType.LISTENING,
    "listening": hikari.ActivityType.LISTENING,
    "play": hikari.ActivityType.PLAYING,
    "playing": hikari.ActivityType.PLAYING,
    "custom": hikari.ActivityType.CUSTOM
}

global activityCycleRunning
activityCycleRunning = True

with open("cfgs/messages.json", "r") as fp:
    raw_status_msgs = json.load(fp)

for message in raw_status_msgs:
    splitMsg = message.split("//")
    bot.d.activityCycle.append([ACTIVITY_ENUMS[splitMsg[0]], splitMsg[1]])

@tasks.task(m=15, auto_start=True)
async def updateStatus():
    if bot.d.activityCycleRunning:
        newStatus = random.choice(bot.d.activityCycle)
        if newStatus[0] == hikari.ActivityType.CUSTOM:
            await bot.update_presence(activity=hikari.Activity(state=newStatus[1], type=hikari.ActivityType.CUSTOM, name=newStatus[1]))
        else:
            await bot.update_presence(activity=hikari.Activity(name=newStatus[1], type=newStatus[0], state=None))

tasks.load(bot)

startupStatus = random.choice(bot.d.activityCycle)
if startupStatus[0] == hikari.ActivityType.CUSTOM:
    startupStatus_STATE = startupStatus[0]
else:
    startupStatus_STATE = None

bot.load_extensions_from(r"./plugins")

# run the bot client.
bot.run(activity=hikari.Activity(name=startupStatus[1], type=startupStatus[0], state=startupStatus_STATE), status=hikari.Status.DO_NOT_DISTURB)
