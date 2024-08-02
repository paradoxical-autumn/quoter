import lightbulb, logging, hikari, miru, sys, asyncio, json

plugin = lightbulb.Plugin("self_destruct", include_datastore=True)

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

class sdCheck(miru.View):
    @miru.button(label="Self destruct", style=hikari.ButtonStyle.DANGER)
    async def reallySelfDestructFrFrOng(self, button: miru.Button, ctx: miru.ViewContext):
        global ranks
        if str(ctx.author.id) in ranks["sd"]:
            await ctx.respond("okay. killing all bot threads. i hope you know what you're doing.")
            await asyncio.sleep(7)
            sys.exit()
        else:
            await ctx.respond("error 403: unauthorised", flags=hikari.MessageFlag.EPHEMERAL)

@plugin.listener(hikari.MessageCreateEvent)
async def onMessage(event: hikari.MessageCreateEvent):
    if event.is_human and event.content:
        me = plugin.bot.get_me()
        if str(event.author_id) == "730089700139991060":
            if event.content == f"{me.mention} sd":
                view = sdCheck(timeout=30)
                await event.message.respond("u sure you wanna make the bot self destruct? this action is irreversible.", components=view)

                event.app.d.miru.start_view(view)
                #await view.wait()
                #await msg.edit("component timed out.", components=None)