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
bot.d.BUILD = "v2024.0803.0"
bot.d.last_module_reboot = math.floor(time.time())

miru.install(bot)
imgtxt.FontDB.SetDefaultEmojiOptions(imgtxt.EmojiOptions(parse_discord_emojis=True))
imgtxt.FontDB.LoadFromDir("./defaultAssets/fonts")

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
