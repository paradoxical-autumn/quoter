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
INSANCE_START_TIME = math.floor(time.time())
USER_PAIR_OFFSET = 128
QUOTE_SIZE = 96
USER_DEETZ_SIZE = 64
QUOTE_PXLS = 900

global last_module_reboot
last_module_reboot = math.floor(time.time())

global build
build = "v2024.0802.0"

dotenv.load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]

# create the bot application
bot = lightbulb.BotApp(BOT_TOKEN, allow_color=False)
miru.install(bot)
imgtxt.FontDB.SetDefaultEmojiOptions(imgtxt.EmojiOptions(parse_discord_emojis=True))
imgtxt.FontDB.LoadFromDir("./defaultAssets/fonts")

# the messages that get displayed when an error occurs
cooldownList = ["HEY!", "Wait up!", ">:C", "a.", ":ice_cube:", ":fire: :fire: :fire:", "Cooldown'd", "Fun remover", ":)", ":nerd: :nerd: :nerd:"]
permissionErrorFlavourText = ["nope.", "I don't think I can do that...", ":nerd:", ":warning:", "oi", "The law requires I answer no.", "`permissionError`", "nuh uh."]
errorFlavourText = ["i didn't touch nothing!", "deleting system 32...", "umm uhh", "im so silly!", "oops...", "i think i dropped something.", "[500] internal server error"]

class bugReportModal(miru.Modal):
    info = miru.TextInput(label="What we're you doing when the error happened?", style=hikari.TextInputStyle.PARAGRAPH, required=True, placeholder="Something like: \"i was just using the bot ;-;\"")
    contact = miru.TextInput(label="Are we allowed to contact you?", style=hikari.TextInputStyle.SHORT, required=True, placeholder="yeah")

    async def callback(self, ctx: miru.ModalContext) -> None:
        embedData = {}

        if ctx.author.avatar_url:
            aviUrl = str(ctx.author.avatar_url)
        else:
            aviUrl = "https://cdn.discordapp.com/embed/avatars/0.png"
        
        embedData["embeds"] = [
            {
                "title": f"New bug report",
                "description": f"from {ctx.author.username}",
                "fields": [
                    {
                        "name": "explanation",
                        "value": self.info.value
                    },
                    {
                        "name": "contact allowed?",
                        "value": self.contact.value
                    }
                ]
            }
        ]

        requests.post(os.environ["ERROR_WEBHOOK"], json=embedData)

        await ctx.respond("sent, thanks for the report!")

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

                        with open("cfgs/messages.json", "r") as fp:
                            raw_status_msgs = json.load(fp)

                        for message in raw_status_msgs:
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
                    await event.message.respond("# admin tools help\n## setting the status\n`<status|broadcast> <playing|watching|listening|custom|reset|reload> [text]`\nsets the status message until the command is run again or `reset` is put as the status mode. `reload` is used to reload the `messages.json` file.\n\n## deleting a response\n-> REPLY\n`delete`\ndeletes a message by quoter.\n## reloading extensions\n`<reboot|reload>`\nreloads all modules (everything except QTR_CORE)\n## installing/uninstalling extensions\n`<install|uninstall> <extension>`\nadds or removes an extension from the bot.")
                
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
                    return
            except IndexError:
                pass

# ping command
@bot.command
@lightbulb.command('ping', 'Ping the bot', ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond(hikari.Embed(title=f"Pong!", color=0xFFB37C).set_footer(f"Running on Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} for {uname.system} {uname.release}"))

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
    helpEmbedData.add_field(name="Disabling the bot", value=f"Use the </settings:1154868394428997672> `[/settings]` panel and go to \"Danger zone\" and click \"Block quotes\"")

    await ctx.respond(helpEmbedData)

# about command
@bot.command
@lightbulb.add_cooldown(7, 1, globalCooldownBucket)
@lightbulb.command('about', 'Information about the bot', ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def about(ctx: lightbulb.context.SlashContext):
    global last_module_reboot
    global build

    aboutEmbedData = hikari.Embed(title="About Quoter",
                                  description=f"made by [paradox](https://github.com/paradoxical-autumn)\n*UGC is not moderated.*",
                                  color=0xFF6D00)
    aboutEmbedData.add_field(name="Useful links", value=f"[Invite link](https://discord.com/oauth2/authorize?client_id=1034045810993803325)\n[Quoter's Website](https://qtr.its-autumn.xyz/#)\n[GitHub repo](https://github.com/paradoxical-autumn/quoter)", inline=True)
    aboutEmbedData.add_field(name="Debugging information", value=f"Build: {build}\nInstance started <t:{INSANCE_START_TIME}:R>\nModules rebooted <t:{last_module_reboot}:R>", inline=True)

    await ctx.respond(aboutEmbedData)

with open("cfgs/messages.json", "r") as fp:
    raw_status_msgs = json.load(fp)

global activityCycle
activityCycle = []

for message in raw_status_msgs:
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
