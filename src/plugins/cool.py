import lightbulb, logging, hikari, miru, sys, asyncio

plugin = lightbulb.Plugin("modal_test", include_datastore=True)

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

class MyModal(miru.Modal, title="Example Title"):

    name = miru.TextInput(
        label="Name",
        placeholder="Type your name!",
        required=True
    )

    bio = miru.TextInput(
        label="Biography",
        value="Pre-filled content!",
        style=hikari.TextInputStyle.PARAGRAPH
    )

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # You can also access the values using ctx.values,
        # Modal.values, or use ctx.get_value_by_id()
        await ctx.respond(
            f"Your name: `{self.name.value}`\nYour bio: ```{self.bio.value}```"
        )

@plugin.command()
@lightbulb.command('wah', "debug command", auto_defer=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def wah(ctx: lightbulb.SlashContext) -> None:
    client: miru.Client = ctx.app.d.miru
    modal = MyModal("EXPLOSION")

    builder = modal.build_response(client)

    await builder.create_modal_response(ctx.interaction)

    client.start_modal(modal)