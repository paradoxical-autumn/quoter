import lightbulb, logging, hikari, miru, sys, asyncio

plugin = lightbulb.Plugin("self_destruct")

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

class sdCheck(miru.View):
    @miru.button(label="Self destruct", style=hikari.ButtonStyle.DANGER)
    async def reallySelfDestructFrFrOng(self, button: miru.Button, ctx: miru.ViewContext):
        if str(ctx.author.id) == "730089700139991060":
            await ctx.respond("okay. killing all bot threads. i hope you know what you're doing.")
            asyncio.sleep(7)
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
                msg = await event.message.respond("u sure you wanna make the bot self destruct? this action is irreversible.", components=view)

                await view.start(msg)
                await view.wait()
                await msg.edit("component timed out.", components=None)