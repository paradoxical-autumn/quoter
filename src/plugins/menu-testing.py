import hikari.events.interaction_events
import lightbulb, hikari, random, logging
import sqlite3 as sql
import hikari, miru
from miru.ext import menu

plugin = lightbulb.Plugin("qtr_SETTINGS_V2", include_datastore=True)

notWindows = True

def load(bot: lightbulb.BotApp):   
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)
    
    global defaultSettings
    with open("cfgs/defaultData") as fp:
        defaultSettings = fp.read()

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

class MainScreen(menu.Screen):
    def __init__(self, menu: menu.Menu) -> None:
        super().__init__(menu)
        self.active_user = menu.active_user

    async def build_content(self) -> menu.ScreenContent:
        conn = sql.connect(r"cfgs/qtr.db")
        conn.commit()

        cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {self.active_user.id}")
        author_data = cur.fetchall()

        if not author_data:
            # it doesnt exist. we need to manually init it.
            global defaultSettings
            _ = conn.execute(defaultSettings, (int(self.active_user.id)))
            conn.commit()
            cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {self.active_user.id}")
            author_data = cur.fetchall()

        # ALWAYS close ur database connections :3
        conn.close()

        # we have the user data!
        self.author_data_tuple = author_data[0]
        front_end_data = f"- Active: {'✅' if self.author_data_tuple[1] == 1 else '❌'}\n- Background: {self.author_data_tuple[3]}\n- DM On Quote: {'✅' if self.author_data_tuple[4] == 1 else '❌'}"

        return menu.ScreenContent(
            embed=hikari.Embed(
                title="Quoter settings",
                description=f"{front_end_data}"
            )
        )

    @menu.button(label="General settings")
    async def pageOne(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await self.menu.push(GeneralSettings(self.menu, self.author_data_tuple))

class GeneralSettings(menu.Screen):
    def __init__(self, menu: menu.Menu, author_dat: tuple) -> None:
        super().__init__(menu)
        dmoq_button: menu.ScreenButton = self.children[1]
        self.author_dat = author_dat

        self.cached_dmoq = self.author_dat[4]
        
        if self.cached_dmoq == 1:
            dmoq_button.style = hikari.ButtonStyle.SUCCESS
            dmoq_button.emoji = "✅"
        elif self.cached_dmoq == 0:
            dmoq_button.style = hikari.ButtonStyle.SECONDARY
            dmoq_button.emoji = "❌"

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent(
            embed=hikari.Embed(
                title="General settings",
                description="General settings for general purposes."
            )
        )
    
    @menu.button(label="back")
    async def back(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await self.menu.pop()
    
    @menu.button(label="DM On Quote", style=hikari.ButtonStyle.SECONDARY)
    async def yipyap(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        conn = sql.connect(r"cfgs/qtr.db")
        conn.commit()
        cur = conn.execute(f"UPDATE settings SET dmOnQuote = {1 - self.cached_dmoq} WHERE settings.id = {ctx.author.id}")
        conn.commit()
        conn.close()

        if (1 - self.cached_dmoq) == 0:
            button.style = hikari.ButtonStyle.SECONDARY
            button.emoji = "❌"
        else:
            button.style = hikari.ButtonStyle.SUCCESS
            button.emoji = "✅"
        
        self.cached_dmoq = 1 - self.cached_dmoq
        
        await self.menu.update_message()

@plugin.command
@lightbulb.command("menu", "demo menu for debugging", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def some_slash_command(ctx: lightbulb.SlashContext) -> None:
    client: miru.Client = ctx.app.d.miru

    my_menu = menu.Menu()  # Create a new Menu
    my_menu.active_user = ctx.author
    # You may need to defer if building your first page takes more than 3 seconds
    builder = await my_menu.build_response_async(client, MainScreen(my_menu), ephemeral=True)
    await builder.create_followup(ctx.interaction)
    # Or if using a prefix command:
    # await builder.send_to_channel(ctx.channel_id)

    client.start_view(my_menu)