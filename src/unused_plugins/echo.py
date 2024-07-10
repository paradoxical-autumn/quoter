import lightbulb, hikari, miru, logging

plugin = lightbulb.Plugin("echo", include_datastore=True)

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

@plugin.listener(hikari.MessageCreateEvent)
async def onMessage(event: hikari.MessageCreateEvent):
    if event.is_human and event.content:
        me = plugin.bot.get_me()
        if str(event.author_id) == "730089700139991060":
            if event.content.lower().startswith(f"{me.mention} echo"):
                splitContent = event.content.split()
                newMsg = ""
                for i in range(2, len(splitContent)):
                    newMsg += f"{splitContent[i]} "
                
                await event.message.respond(newMsg)