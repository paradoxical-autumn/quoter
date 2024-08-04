import lightbulb, logging, miru, sys, asyncio
import hikari

plugin = lightbulb.Plugin("error_out", include_datastore=True)

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

error_parsers = {
    "EOFError": EOFError,
    "ForbiddenError": hikari.errors.ForbiddenError(url="https://qtr.its-autumn.xyz/", raw_body="manually caused debug crash", headers=[]),
    "UnauthorizedError": hikari.errors.UnauthorizedError(url="https://qtr.its-autumn.xyz/", raw_body="manually caused debug crash", headers=[]),
    "NotFoundError": hikari.errors.NotFoundError(url="https://qtr.its-autumn.xyz/", raw_body="manually caused debug crash", headers=[])
}

@plugin.command
@lightbulb.option("error_type", "The type of error to cause", type=str, choices=["EOFError", "ForbiddenError", "UnauthorizedError", "NotFoundError"])
@lightbulb.command('error', "cause an error for debugging", auto_defer=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def error_out(ctx: lightbulb.SlashContext) -> None:
    if ctx.options.error_type in error_parsers:
        raise error_parsers[ctx.options.error_type]
    else:
        raise TypeError("Not a valid exception type")