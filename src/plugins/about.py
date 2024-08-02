import hikari, lightbulb, logging, sys
from platform import uname

plugin = lightbulb.Plugin("qtr_about", include_datastore=True)

def load(bot: lightbulb.BotApp):   
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

@plugin.command()
@lightbulb.command("about", "Information about the bot", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def about(ctx: lightbulb.context.SlashContext):
    aboutEmbedData = hikari.Embed(title="About Quoter",
                                  description=f"made by [paradox](https://github.com/paradoxical-autumn)\n*UGC is not moderated.*",
                                  color=0xFF6D00)
    aboutEmbedData.add_field(name="Useful links", value=f"[Invite link](https://discord.com/oauth2/authorize?client_id=1034045810993803325)\n[Quoter's Website](https://qtr.its-autumn.xyz/#)\n[GitHub repo](https://github.com/paradoxical-autumn/quoter)", inline=True)
    aboutEmbedData.add_field(name="Debugging information", value=f"QTRCore Build: {plugin.bot.d.BUILD}\nInstance started <t:{plugin.bot.d.INSTANCE_START_TIME}:R>\nModules rebooted <t:{plugin.bot.d.last_module_reboot}:R>", inline=True)

    await ctx.respond(aboutEmbedData)

@plugin.command()
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

@plugin.command
@lightbulb.command('ping', 'Ping the bot', ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond(hikari.Embed(title=f"Pong!", color=0xFFB37C).set_footer(f"Running on Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} for {uname.system} {uname.release}"))
