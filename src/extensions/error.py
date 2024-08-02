import lightbulb, logging, hikari, miru, sys, asyncio

plugin = lightbulb.Plugin("error_out", include_datastore=True)

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

@plugin.command
@lightbulb.command('error', "cause an error for debugging", auto_defer=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def error_out(ctx: lightbulb.SlashContext) -> None:
    raise EOFError("Not implemented.")