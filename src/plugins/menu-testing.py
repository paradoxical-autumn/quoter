from typing import Coroutine
import lightbulb, os, json, hikari, random, logging
from PIL import Image
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
        # grab the user data
        conn = sql.connect(r"cfgs/qtr.db")
        conn.commit()

        cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {menu.active_user.id}")
        author_data = cur.fetchall()

        if not author_data:
            # it doesnt exist. we need to manually init it.
            global defaultSettings
            _ = conn.execute(defaultSettings, (int(menu.active_user.id)))
            conn.commit()
            cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {menu.active_user.id}")
            author_data = cur.fetchall()

        # ALWAYS close ur database connections :3
        conn.close()

        # we have the user data!
        self.author_data_tuple = author_data[0]
        self.front_end_data = f"- Active: {'✅' if self.author_data_tuple[1] == 1 else '❌'}\n- Background: {self.author_data_tuple[3]}\n- DM On Quote: {'✅' if self.author_data_tuple[4] == 1 else '❌'}"

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent(
            embed=hikari.Embed(
                title="Quoter settings",
                description=f"{self.front_end_data}"
            )
        )

    @menu.button(label="page1")
    async def pageOne(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await self.menu.push(screenOne(self.menu))
    
    @menu.button(label="screen two")
    async def pageTwo(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await self.menu.push(screenTwo(self.menu))

class screenOne(menu.Screen):
    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent(
            embed=hikari.Embed(
                title="Screen one",
                description="Welcome to screen one!"
            )
        )
    
    @menu.button(label="back")
    async def back(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await self.menu.pop()
    
    @menu.button(label="YIPPEE", style=hikari.ButtonStyle.SUCCESS)
    async def yipyap(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await ctx.respond("hoi guys.")

class screenTwo(menu.Screen):
    def __init__(self, menu: menu.Menu) -> None:
        super().__init__(menu)
        self.is_enabled = False
    
    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent(
            embed=hikari.Embed(
                title="screen two",
                description="WOAH THERE'S A SECOND?"
            )
        )
    
    @menu.button(label="back")
    async def back(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await self.menu.pop()
    
    @menu.button(label="enable", style=hikari.ButtonStyle.DANGER)
    async def enable(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        self.is_enabled = not self.is_enabled

        if self.is_enabled:
            button.style = hikari.ButtonStyle.SUCCESS
            button.label = "disable"
        else:
            button.style = hikari.ButtonStyle.DANGER
            button.label = "enable"
        
        await self.menu.update_message()

@plugin.command
@lightbulb.command("menu", "demo menu for debugging", auto_defer=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def some_slash_command(ctx: lightbulb.SlashContext) -> None:
    client: miru.Client = ctx.app.d.miru

    my_menu = menu.Menu()  # Create a new Menu
    my_menu.active_user = ctx.author
    # You may need to defer if building your first page takes more than 3 seconds
    builder = await my_menu.build_response_async(client, MainScreen(my_menu))
    await builder.create_initial_response(ctx.interaction)
    # Or if using a prefix command:
    # await builder.send_to_channel(ctx.channel_id)

    client.start_view(my_menu)