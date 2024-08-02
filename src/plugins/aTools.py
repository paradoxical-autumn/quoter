import hikari, lightbulb, json, logging, random, math, time

plugin = lightbulb.Plugin("qtr_aTools", include_datastore=True)

def load(bot: lightbulb.BotApp):
    global ranks

    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)
    
    try:
        with open("cfgs/ranks.json", "r") as fp:
            ranks = json.load(fp)
    except FileNotFoundError:
        logging.critical("Unable to load ranks file. ATools is disabled.")
        bot.remove_plugin(plugin)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

# bot.d.activityCycleRunning
ACTIVITY_ENUMS = {
    "watch": hikari.ActivityType.WATCHING,
    "watching": hikari.ActivityType.WATCHING,
    "listen": hikari.ActivityType.LISTENING,
    "listening": hikari.ActivityType.LISTENING,
    "play": hikari.ActivityType.PLAYING,
    "playing": hikari.ActivityType.PLAYING,
    "custom": hikari.ActivityType.CUSTOM
}

@plugin.listener(hikari.events.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):
    global ranks
    if not event.is_human:
        return
    
    me = plugin.bot.get_me()

    if me.id not in event.message.user_mentions_ids:
        return
    
    if not event.content.startswith(me.mention):
        return
    
    if str(event.author.id) not in ranks["devTools"]:
        return
    
    split_msg = event.message.content.split(" ")
    try:
        if split_msg[1].lower() == "status" or split_msg[1].lower() == "broadcast":
            if split_msg[2].lower() not in ACTIVITY_ENUMS and split_msg[2].lower() != "reset" and split_msg[2].lower() != "reload":
                await event.message.respond("yo that's not an activity type\ntry: watching, playing or listening (since others arent supported)")

                return
            elif split_msg[2].lower() == "reset":
                newStatus = random.choice(plugin.bot.d.activityCycle)
                if newStatus[0] == hikari.ActivityType.CUSTOM:
                    await plugin.bot.update_presence(activity=hikari.Activity(state=newStatus[1], type=hikari.ActivityType.CUSTOM, name=newStatus[1]))
                else:
                    await plugin.bot.update_presence(activity=hikari.Activity(name=newStatus[1], type=newStatus[0], state=None))
                plugin.bot.d.activityCycleRunning = True
                await event.message.respond("reset the status")

                return
            elif split_msg[2].lower() == "reload":
                plugin.bot.d.activityCycle = []

                with open("cfgs/messages.json", "r") as fp:
                    raw_status_msgs = json.load(fp)

                for message in raw_status_msgs:
                    splitMsg = message.split("//")
                    plugin.bot.d.activityCycle.append([ACTIVITY_ENUMS[splitMsg[0]], splitMsg[1]])

                await event.message.respond("reloaded the status cycle")
                return
            else:
                plugin.bot.d.activityCycleRunning = False
                activityType = ACTIVITY_ENUMS[split_msg[2]]
            status = ""
            for i in range(3, len(split_msg)):
                status += f"{split_msg[i]} "
            
            if activityType == hikari.ActivityType.CUSTOM:
                newState = status.strip(" ")
                newName = status.strip(" ")
            else:
                newState = None
                newName = status.strip(" ")

            await plugin.bot.update_presence(activity=hikari.Activity(name=newName, type=activityType, state=newState))
            await event.message.respond(f"updated status to: `{split_msg[2]}` {status.strip(' ')}")
        elif split_msg[1].lower() == "delete":
            try:
                await event.message.referenced_message.delete()
            except hikari.ForbiddenError:
                await event.message.respond("error 403")
            except AttributeError:
                await event.message.respond("reply to a message to delete it.")
        elif split_msg[1].lower() == "help":
            await event.message.respond("# admin tools help\n## setting the status\n`<status|broadcast> <playing|watching|listening|custom|reset|reload> [text]`\nsets the status message until the command is run again or `reset` is put as the status mode. `reload` is used to reload the `messages.json` file.\n\n## deleting a response\n-> REPLY\n`delete`\ndeletes a message by quoter.\n## reloading extensions\n`<reboot|reload>`\nreloads all modules (everything except QTR_CORE)\n## installing/uninstalling extensions\n`<install|uninstall> <extension>`\nadds or removes an extension from the bot.")
        
        elif split_msg[1].lower() == "reboot" or split_msg[1].lower() == "reload":
            for _ in plugin.bot.extensions:
                plugin.bot.reload_extensions(*plugin.bot.extensions)
            await event.message.respond("reloaded extension libraries")
            plugin.bot.d.last_module_reboot = math.floor(time.time())
        
        elif split_msg[1].lower() == "install":
            try:
                plugin.bot.load_extensions(split_msg[2])
                await event.message.respond("installed.")
            except IndexError:
                await event.message.respond("you have to say an extension name to install it lmao")
            except lightbulb.errors.ExtensionNotFound:
                await event.message.respond("that's not a valid extension name smh")
            except lightbulb.errors.ExtensionAlreadyLoaded:
                await event.message.respond("that extension is already loaded...")
            
        elif split_msg[1].lower() == "uninstall":
            try:
                plugin.bot.unload_extensions(split_msg[2])
                await event.message.respond("uninstalled.")
            except IndexError:
                await event.message.respond("you have to say an extension name to install it lmao")
            except lightbulb.errors.ExtensionNotLoaded:
                await event.message.respond("that extension isn't installed.")
        else:
            return
    except IndexError:
        # ¯\_(ツ)_/¯
        pass