# imports
from PIL import Image, ImageDraw, ImageFont
import os
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
ALERTS_HOOK = "https://canary.discord.com/api/webhooks/1117139818447646732/MAe-7s2mJRv1f-3OsuJT3ErW6MEFAXqdceV6sABP0Na9MTdjZVSel_nEY_6MnIwrmJfF"
INSANCE_START_TIME = math.floor(time.time())
USER_PAIR_OFFSET = 128
QUOTE_SIZE = 96
USER_DEETZ_SIZE = 64
QUOTE_PXLS = 900

global last_module_reboot
last_module_reboot = math.floor(time.time())

global build
build = "v3.0.1"

IS_BETA = True
dotenv.load_dotenv()
if IS_BETA:
    logging.warning("// RUNNING IN BETA MODE //")
    BOT_TOKEN = os.environ["CANARY_TOKEN"]
else:
    BOT_TOKEN = os.environ["BOT_TOKEN"]

def exitProtocols():
    embedData = {}
    embedData["embeds"] = [
        {
            "description": "ouch the server died. someone yell at autumn kthxbye",
            "title": "Quoter died, soz bout that.",
            "color": 0xff6d71,
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }
    ]
    requests.post(ALERTS_HOOK, json = embedData)

if not IS_BETA:
    atexit.register(exitProtocols)

# create the bot application
bot = lightbulb.BotApp(BOT_TOKEN, allow_color=False)
miru.install(bot)
imgtxt.FontDB.SetDefaultEmojiOptions(imgtxt.EmojiOptions(parse_discord_emojis=True))
imgtxt.FontDB.LoadFromDir("./defaultAssets/fonts")

# the messages that get displayed when an error occurs
cooldownList = ["HEY!", "Wait up!", ">:C", "a.", ":ice_cube:", ":fire: :fire: :fire:", "Cooldown'd", "Fun remover", "Prevent crashing Autumn's drive Inator", ":)", ":nerd: :nerd: :nerd:"]
permissionErrorFlavourText = ["Someone's been naughty!", "nope.", "I don't think I can do that...", ":nerd:", ":warning:", "oi", "The law requires I answer no.", "`permissionError`"]
errorFlavourText = ["i didn't touch nothing!", "deleting system 32...", "umm uhh", "im so silly!", "oops...", "i think i dropped something.", "[500] internal server error"]


global cleanedBannedWords
cleanedBannedWords = []

"""
with open("cfgs/profanity_filter.wlist", "r", encoding="utf-8") as fp:
    bannedWords = fp.readlines()
    
    for i in bannedWords:
        i = i.lower()
        i = i.strip("\n")
        cleanedBannedWords.append(i)
"""

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
                "description": f"{event.exception.original}",
                "title": "quoter broke (again).",
                "color": 0xED4245,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "footer": {
                    "text": f"{event.context.author.global_name} // @{event.context.author.username}",
                    "icon_url": aviUrl
                }
            }
        ]

        requests.post("https://canary.discord.com/api/webhooks/1122518470899286116/L15uhB_gf2OuxWIz5lb-kROHu4XpcYak3CaaxVi_lW9yzvyelxAh2LXwWMZjE1cyuTrZ", json=errorEmbedData)
        # await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`.")
        await event.context.respond(hikari.Embed(title=f"[500] Internal Server error", description=f"An error occurred.", color=0xED4245))
        logging.fatal(f"{event.exception.original}")

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond(hikari.Embed(title=f"[401] Unauthorised", description=":no_entry_sign: You don't have authorisation to run that command!", color=0xFEE75C))

    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(hikari.Embed(title="[429] Too many requests", description=f"Retry after `{exception.retry_after:.2f}` seconds.", color=0x5865F2))

    elif ...:
        ...
    else:
        raise exception

#input("Suspended.")

# create a function to wrap the words.
"""
def wrap_words(string, chars):
    textLists = tw(width=chars, max_lines=14).wrap(string)
    ret = ''

    for i in textLists:
        ret += i + "\n"
    return ret
"""

# init cooldowns
quoteCooldownBucket = lightbulb.buckets.UserBucket
globalCooldownBucket = lightbulb.buckets.UserBucket
feedBackCooldownBucket = lightbulb.buckets.UserBucket

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

###############
# ADMIN TOOLS #
###############

global activityCycleRunning
activityCycleRunning = True

@bot.listen(hikari.events.MessageCreateEvent)
async def adminTools(event: hikari.MessageCreateEvent):
    if not event.is_human:
        return
    
    me = bot.get_me()

    if me.id in event.message.user_mentions_ids and event.message.content.startswith(me.mention):
        if str(event.author.id) in ranks["devTools"]:
            """
            response = await event.message.respond("Hello cringe department? I'd like to file a claim!")

            await asyncio.sleep(7)

            await response.delete()
            """

            splitMessage = event.message.content.split(" ")
            try:
                if splitMessage[1].lower() == "status" or splitMessage[1].lower() == "broadcast":
                    global activityCycle
                    global activityCycleRunning
                    if splitMessage[2].lower() not in ACTIVITY_ENUMS and splitMessage[2].lower() != "reset" and splitMessage[2].lower() != "reload":
                        await event.message.respond("yo that's not an activity type\ntry: watching, playing or listening (since others arent supported)")

                        return
                    elif splitMessage[2].lower() == "reset":
                        newStatus = random.choice(activityCycle)
                        if newStatus[0] == hikari.ActivityType.CUSTOM:
                            await bot.update_presence(activity=hikari.Activity(state=newStatus[1], type=hikari.ActivityType.CUSTOM, name=newStatus[1]))
                        else:
                            await bot.update_presence(activity=hikari.Activity(name=newStatus[1], type=newStatus[0], state=None))
                        activityCycleRunning = True
                        await event.message.respond("reset the status")

                        return
                    elif splitMessage[2].lower() == "reload":
                        activityCycle = []

                        for message in RAW_MESSAGES:
                            splitMsg = message.split("//")
                            activityCycle.append([ACTIVITY_ENUMS[splitMsg[0]], splitMsg[1]])

                        await event.message.respond("reloaded the status cycle")
                        return
                    else:
                        activityCycleRunning = False
                        activityType = ACTIVITY_ENUMS[splitMessage[2]]
                    status = ""
                    for i in range(3, len(splitMessage)):
                        status += f"{splitMessage[i]} "
                    
                    if activityType == hikari.ActivityType.CUSTOM:
                        newState = status.strip(" ")
                        newName = status.strip(" ")
                    else:
                        newState = None
                        newName = status.strip(" ")

                    await bot.update_presence(activity=hikari.Activity(name=newName, type=activityType, state=newState))
                    await event.message.respond(f"updated status to: `{splitMessage[2]}` {status.strip(' ')}")
                elif splitMessage[1].lower() == "delete":
                    try:
                        await event.message.referenced_message.delete()
                    except hikari.ForbiddenError:
                        await event.message.respond("error 403")
                    except AttributeError:
                        await event.message.respond("reply to a message to delete it.")
                elif splitMessage[1].lower() == "help":
                    await event.message.respond("# admin tools help\n## setting the status\n`<status|broadcast> <playing|watching|listening|custom|reset> [text]>`\nsets the status message until the command is run again or `reset` is put as the status\n\n## deleting a response\n-> REPLY\n`delete`\ndeletes a message by quoter.\n## reloading extensions\n`<reboot|reload>`\nreloads all modules (everything except QTR_CORE)\n## installing/uninstalling extensions\n`<install|uninstall> <extension>`\nadds or removes an extension from the bot.")
                
                elif splitMessage[1].lower() == "reboot" or splitMessage[1].lower() == "reload":
                    for _ in bot.extensions:
                        bot.reload_extensions(*bot.extensions)
                    await event.message.respond("reloaded extension libraries")
                    global last_module_reboot
                    last_module_reboot = math.floor(time.time())
                
                elif splitMessage[1].lower() == "install":
                    try:
                        bot.load_extensions(splitMessage[2])
                        await event.message.respond("installed.")
                    except IndexError:
                        await event.message.respond("you have to say an extension name to install it lmao")
                    except lightbulb.errors.ExtensionNotFound:
                        await event.message.respond("that's not a valid extension name smh")
                    except lightbulb.errors.ExtensionAlreadyLoaded:
                        await event.message.respond("that extension is already loaded...")
                    
                elif splitMessage[1].lower() == "uninstall":
                    try:
                        bot.unload_extensions(splitMessage[2])
                        await event.message.respond("uninstalled.")
                    except IndexError:
                        await event.message.respond("you have to say an extension name to install it lmao")
                    except lightbulb.errors.ExtensionNotLoaded:
                        await event.message.respond("that extension isn't installed.")
                else:
                    await event.message.respond("error: unknown command.")
                    return
            except IndexError:
                pass

# ping command
@bot.command
@lightbulb.command('ping', 'Ping the bot', ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond(hikari.Embed(title=f"Pong!", color=0xFFB37C).set_footer(f"Running on Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} for {uname.system} {uname.release}"))

class feedBackModal(miru.Modal):
    feedbackType = miru.TextInput(label="What type of feedback?", style=hikari.TextInputStyle.SHORT, required=True, placeholder="Suggestion, bug report or something else?")
    actualFeedback = miru.TextInput(label="Feedback:", style=hikari.TextInputStyle.PARAGRAPH, required=True, placeholder="Enter your feedback here!")
    
    async def callback(self, ctx: miru.ModalContext) -> None:
        try:
            with open("cfgs/feedbackBans.json", "r") as fp:
                feedbackbans = json.load(fp)
        except Exception as err:
            print(f"{'[Unable to get feedback bans]':=^50}")
            print(f"Why? -> {err}")
            if not os.path.isdir("cfgs"):
                os.mkdir("cfgs")
    
            feedbackbans = []
            with open("cfgs/feedbackBans.json", "w") as fp:
                json.dump(feedbackbans, fp, indent=4)
        
        if ctx.author.id in feedbackbans:
            await ctx.respond(hikari.Embed(title=f"Banned", description=f"You're banned from submitting feedback."), flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        if ctx.author.avatar_url:
            aviUrl = str(ctx.author.avatar_url)
        else:
            aviUrl = "https://cdn.discordapp.com/attachments/907681321718009866/1122545490731487254/quoter_-_please_do_not_publically_use_this_image.png"
        
        if ctx.author.global_name:
            nickname = ctx.author.global_name
        else:
            nickname = ctx.author.username

        await ctx.respond(f"Thanks for the feedback!", flags=hikari.MessageFlag.EPHEMERAL)
        feedbackEmbedData = {
            "username": nickname,
            "avatar_url": aviUrl,
        }
        feedbackEmbedData["embeds"] = [
            {
                "title": "Quoter feedback received.",
                "color": 0x414141,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "fields": [
                    {
                        "name": "Context:",
                        "value": f"Sent by @{ctx.author.username}\nTheir ID: `{ctx.author.id}`\nType: {self.feedbackType.value}",
                        "inline": True
                    },
                    {
                        "name": "Feedback:",
                        "value": f"{self.actualFeedback.value}",
                        "inline": True
                    }
                ]
            }
        ]
        requests.post("https://canary.discord.com/api/webhooks/1122536317989949452/bcKEm97V4w5oUIA2-zl2WofQAyfVDpsv8Tz4wGqTqe3qtJKAhi6n_yObtqLPOvX4X3J9", json=feedbackEmbedData)

class aboutAndHelpButtons(miru.View):
    @miru.button(label="Give feedback", style=hikari.ButtonStyle.SECONDARY)
    async def feedbackButton(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = feedBackModal(title="Quoter Feedback")
        await ctx.respond_with_modal(modal)

# help command
@bot.command
@lightbulb.add_cooldown(7, 1, globalCooldownBucket)
@lightbulb.command('help', 'How to use the bot', ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def help(ctx):
    helpEmbedData = hikari.Embed(title="Help!",
                                 description="Quoter is pretty easy to use but here are some guides!",
                                 color=0x00FF00)
    helpEmbedData.add_field(name="Basic usage", value="1. Right click on a message (or hold down on mobile)\n2. Go to Apps\n3. Hit \"Quote\" (the one with the bot's icon!)", inline=True)
    helpEmbedData.add_field(name="Custom usage", value="You can use </custom:1104511640466108506> `[/custom]` to make a custom quote. These are tagged as \"Unofficial\" because they can't be verified.", inline=True)
    helpEmbedData.add_field(name="Opting out/in", value=f"There's a button attached to /about, you can use that.")

    await ctx.respond(helpEmbedData)

# about command
@bot.command
@lightbulb.add_cooldown(7, 1, globalCooldownBucket)
@lightbulb.command('about', 'Information about the bot', ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def about(ctx: lightbulb.context.SlashContext):
    global last_module_reboot
    global build
    view = aboutAndHelpButtons(timeout=60)

    aboutEmbedData = hikari.Embed(title="About Quoter",
                                  description=f"© Autumn 2023\n*UGC is not moderated.*",
                                  color=0xFF6D00)
    aboutEmbedData.add_field(name="Invite links", value="[Application & Bot user (Recommended)](https://discord.com/api/oauth2/authorize?client_id=1034045810993803325&permissions=274877959168&scope=applications.commands%20bot)\n\n[Application (If you don't want the app added as a member)](https://discord.com/api/oauth2/authorize?client_id=1034045810993803325&scope=applications.commands)", inline=True)
    aboutEmbedData.add_field(name="Debugging information", value=f"Build: {build}\nInstance started <t:{INSANCE_START_TIME}:R>\nModules rebooted <t:{last_module_reboot}:R>", inline=True)
    aboutEmbedData.add_field(name="Useful links", value=f"[Quoter's Website](https://qtr.its-autumn.xyz/#)\nSupport serving [COMING SOON]", inline=True)

    message = await ctx.respond(aboutEmbedData, components=view)
    await view.start(message)

    await view.wait()

    aboutEmbedData.add_field(name="Timed out", value="The buttons attached to this message have timed out. Re-run the command if you need them.")

    view.feedbackButton.disabled = True

    await message.edit(aboutEmbedData, components=view)

class reportModal(miru.Modal):
    why = miru.TextInput(label="Why are you reporting them?", style=hikari.TextInputStyle.SHORT, required=True)

    async def callback(self, ctx: miru.ModalContext) -> None:
        #await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)
        response = await ctx.respond("Sending report...", flags=hikari.MessageFlag.EPHEMERAL)

        #qtDl = Image.open(requests.get(f"{self.attachment}", stream=True).raw)
        #reportName = ""
        #for _ in range(16):
        #    reportName += random.choice(string.ascii_letters)

        #qtDl.save(rf"outputs/SPOILER_R_{reportName}.png")
        reportEmbedData = {}
        reportEmbedData["embeds"] = [
            {
                "title": "Report received",
                "color": 0xFF0000,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "image": {
                    "url": str(self.attachment)
                },
                "description": f"{self.messageContent.content}",
                "fields":  [
                    {
                        "name": "Report info",
                        "value": f"{self.why.value}",
                        "inline": True
                    },
                    {
                        "name": "Context",
                        "value": f"`{self.messageContent.content}`\n\nReported by {self.reportAuthor.username} `{self.reportAuthor.id}`",
                        "inline": True
                    }
                ]
            }
        ]

        # this version creates a clone of the image
        #reportResponse = requests.post(r"https://canary.discord.com/api/webhooks/1152022137658421279/pPjZ6_g9M5GfOs1JMvxi4k83GUkuKSV2O8BuP1M-1i_-SzwAq3r2AESm3HOrVDMqpuwL", data={"content": f"# New report\n||{self.reportAuthor.username} (`{self.reportAuthor.id}`)|| said ||{self.why.value}||\n### Message content:\n{self.messageContent.content}"}, files={"file": open(f"outputs/SPOILER_R_{reportName}.png", "rb")})
        
        # this version uses the currently uploaded one
        reportResponse = requests.post(r"https://canary.discord.com/api/webhooks/1152022137658421279/pPjZ6_g9M5GfOs1JMvxi4k83GUkuKSV2O8BuP1M-1i_-SzwAq3r2AESm3HOrVDMqpuwL", json=reportEmbedData)

        if reportResponse.status_code == 204 or reportResponse.status_code == 200:
            await response.edit("Report sent.")
        else:
            await response.edit(f"Error sending report.")
            print(reportResponse.status_code)
            print(reportResponse.text)
        
        #os.remove(f"outputs/SPOILER_R_{reportName}.png")

class reportView(miru.View):
    @miru.button(style=hikari.ButtonStyle.DANGER, label="Report")
    async def yesReport(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = reportModal(title="Report quote")
        modal.attachment = str(self.attachment)
        modal.messageContent = self.messageContent
        modal.reportAuthor = ctx.author
        await ctx.respond_with_modal(modal)

# report system
@bot.command
@lightbulb.add_cooldown(300, 1, globalCooldownBucket)
@lightbulb.command('Report quote', 'Report a user\'s quote.', ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.MessageCommand)
async def reportQt(ctx: lightbulb.Context):
    me = bot.get_me()
    if ctx.options.target.author.id == me.id:
        if ctx.options.target.attachments:
            view = reportView()
            view.messageContent = ctx.options.target
            view.attachment = ctx.options.target.attachments[0].url
            view.reportAuthor = ctx.author

            msg = await ctx.respond("Are you sure you wanna report this message?\nThis WILL:\n- Send the quote\n- Send YOUR user information\n- Send THEIR user information\n- Send whether the quote was official or not\n\nBy reporting you also confirm that it is truthful and made in good faith. Please also do not submit false, duplicate or test reports.", components=view)

            await view.start(msg)
        else:
            await ctx.respond("It doesn't look like that's a quote?")
    else:
        await ctx.respond("You can only report messages sent by me. If you use Quoter PTB/Canary, please report using that.")

embedData = {}

embedData["embeds"] = [
    {
        "description": "that's was unexpected.",
        "title": "woah the code actually booted up.",
        "color": 0x71ff6d,
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    }
]

if not IS_BETA:
    requests.post(ALERTS_HOOK, json=embedData)

with open("cfgs/messages.json", "r") as fp:
    RAW_MESSAGES = json.load(fp)

global activityCycle
activityCycle = []

for message in RAW_MESSAGES:
    splitMsg = message.split("//")
    activityCycle.append([ACTIVITY_ENUMS[splitMsg[0]], splitMsg[1]])

@tasks.task(m=15, auto_start=True)
async def updateStatus():
    global activityCycleRunning
    if activityCycleRunning:
        newStatus = random.choice(activityCycle)
        if newStatus[0] == hikari.ActivityType.CUSTOM:
            await bot.update_presence(activity=hikari.Activity(state=newStatus[1], type=hikari.ActivityType.CUSTOM, name=newStatus[1]))
        else:
            await bot.update_presence(activity=hikari.Activity(name=newStatus[1], type=newStatus[0], state=None))

tasks.load(bot)

startupStatus = random.choice(activityCycle)
if startupStatus[0] == hikari.ActivityType.CUSTOM:
    startupStatus_STATE = startupStatus[0]
else:
    startupStatus_STATE = None

bot.load_extensions_from(r"./plugins")

# run the bot client.
bot.run(activity=hikari.Activity(name=startupStatus[1], type=startupStatus[0], state=startupStatus_STATE), status=hikari.Status.DO_NOT_DISTURB)
