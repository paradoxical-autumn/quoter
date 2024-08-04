import hikari, lightbulb, miru, requests, logging, os, random, traceback
from datetime import datetime

plugin = lightbulb.Plugin("qtr_handlers", include_datastore=True)

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

cooldownList = ["HEY!", "Wait up!", ">:C", "a.", ":ice_cube:", ":fire: :fire: :fire:", "Cooldown'd", "Fun remover", ":)", ":nerd: :nerd: :nerd:"]
permissionErrorFlavourText = ["nope.", "I don't think I can do that...", ":nerd:", ":warning:", "oi", "The law requires I answer no.", "`permissionError`", "nuh uh."]
errorFlavourText = ["i didn't touch nothing!", "deleting system 32...", "umm uhh", "im so silly!", "oops...", "i think i dropped something.", "[500] internal server error"]

class bugReportView(miru.View):
    pass

@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        tb_str = traceback.format_exception(type(event.exception.original), value=event.exception.original, tb=event.exception.original.__traceback__)

        fmt_trcbk = ""
        tbi = tb_str[-2].replace("\\n", "\n")
        tbi = tbi.strip()
        fmt_trcbk += tbi

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
                    },
                    {
                        "name": "traceback information",
                        "inline": True,
                        "value": f"`{fmt_trcbk}`"
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
                await event.context.respond(hikari.Embed(title="[401] Unauthorized", description=f"An authorization error occurred. Please try again. If it still isn't working, try it in a different channel/server.", color=0xED4245), components=view)
            except:
                try:
                    await event.context.user.send("# Sorry!\nIt looks like you recently tried to use a command which was 401'd. Maybe try again?\n\nIf it is still being 401'd after that:\n- Try it in a different channel/server\n- Consider filing a bug report at <https://github.com/paradoxical-autumn/quoter/issues>")
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