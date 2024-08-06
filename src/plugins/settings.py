import lightbulb, os, json, hikari, random, logging
from PIL import Image
import sqlite3 as sql
import hikari, miru

plugin = lightbulb.Plugin("qtr_SETTINGS", include_datastore=True)

notWindows = True
qtr_COOLDOWN = lightbulb.buckets.UserBucket

def load(bot: lightbulb.BotApp):
    global qtRatios
    with open("cfgs/qtMsgs.json", "r") as fp:
        qtRatios = json.load(fp)
    
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)
    
    global defaultSettings
    with open("cfgs/defaultData") as fp:
        defaultSettings = fp.read()

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

class generalSettings(miru.View):
    @miru.button(label="DM On Quote", style=hikari.ButtonStyle.SECONDARY)
    async def toggleDMOnQ(self, ctx: miru.ViewContext, button: miru.Button):
        conn = sql.connect(r"cfgs/qtr.db")

        conn.commit()

        cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.author.id}")

        authorData = cur.fetchall()

        if not authorData:
            global defaultSettings
            _ = conn.execute(defaultSettings, (int(ctx.author.id),))
            conn.commit()
            cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.author.id}")
            authorData = cur.fetchall()

        conn.close()
        authorDataTuple = authorData[0]

        if authorDataTuple[4] == False:
            button.style = hikari.ButtonStyle.SUCCESS
            button.emoji = "✅"
            conn = sql.connect(r"cfgs/qtr.db")

            conn.commit()

            cur = conn.execute(f"UPDATE settings SET dmOnQuote = 1 WHERE settings.id = {ctx.author.id}")

            conn.commit()

            conn.close()
            await ctx.edit_response("Enabled DM On Quote", components=self)
        else:
            button.style = hikari.ButtonStyle.DANGER
            button.emoji = "✖️"
            conn = sql.connect(r"cfgs/qtr.db")

            conn.commit()

            cur = conn.execute(f"UPDATE settings SET dmOnQuote = 0 WHERE settings.id = {ctx.author.id}")

            conn.commit()

            conn.close()
            await ctx.edit_response("Disabled DM On Quote", components=self)

class dangerousSettings(miru.View):
    @miru.button(label="Block processing", style=hikari.ButtonStyle.SECONDARY)
    async def disable(self, ctx: miru.ViewContext, button: miru.Button):
        self.mainSettings: hikari.Message

        await self.mainSettings.edit("This menu is no longer available.", components=None)
        conn = sql.connect(r"cfgs/qtr.db")

        conn.commit()

        cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.author.id}")

        authorData = cur.fetchall()

        if not authorData:
            global defaultSettings
            _ = conn.execute(defaultSettings, (int(ctx.author.id),))
            conn.commit()
            cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.author.id}")
            authorData = cur.fetchall()

        conn.close()
        authorDataTuple = authorData[0]

        conn = sql.connect(r"cfgs/qtr.db")

        conn.commit()

        if authorDataTuple[1]:
            cur = conn.execute(f"UPDATE settings SET active = 0 WHERE id = {ctx.author.id}")
            conn.commit()

            await ctx.edit_response("Your data is no longer being processed. You can unblock processing whenever you want.", components=None)
        else:
            cur = conn.execute(f"UPDATE settings SET active = 1 WHERE id = {ctx.author.id}")
            conn.commit()

            await ctx.edit_response("Welcome back!", components=None)

class customBgHandler(miru.Modal):
    imageUrl = miru.TextInput(label="Image URL", style=hikari.TextInputStyle.PARAGRAPH, required=True, placeholder="The link to your custom quote background")
    async def callback(self, ctx: miru.ModalContext) -> None:
        conn = sql.connect(r"cfgs/qtr.db")
        conn.commit()
        cur = conn.execute(f"UPDATE settings SET customBg = ? WHERE settings.id = {ctx.author.id}", (self.imageUrl.value,))
        conn.commit()
        await ctx.respond(f"updated custom background to: {self.imageUrl.value}", flags=hikari.MessageFlag.EPHEMERAL)

class settingsView(miru.View):
    @miru.text_select(
        placeholder="Select a page!",
        options=[
            miru.SelectOption(label="General", value="general", description="General settings"),
            miru.SelectOption(label="Select background", value="custom", description="Stuff like setting your background"),
            miru.SelectOption(label="Danger zone", value="danger", description="Stuff like disabling your account!")
        ]
    )
    async def option(self, select: miru.TextSelect, ctx: miru.ViewContext):
        message: hikari.Message
        message = self.response
        userData = self.userData

        if select.values[0] == "general":
            view = generalSettings()
            if userData[4]:
                view.toggleDMOnQ.style = hikari.ButtonStyle.SUCCESS
                view.toggleDMOnQ.emoji = "✅"
            else:
                view.toggleDMOnQ.style = hikari.ButtonStyle.DANGER
                view.toggleDMOnQ.emoji = "✖️"
            await ctx.respond("General settings", flags=hikari.MessageFlag.EPHEMERAL, components=view)

            plugin.d.miru.start_view(view)
            #await view.wait()
            #await generalMsg.edit("This object has timed out.", components=None)
            
        elif select.values[0] == "custom":
            if userData[5] == 0:
                await ctx.respond("You don't have any custom backgrounds <:feelsBadMan:1154514899242848256>", flags=hikari.MessageFlag.EPHEMERAL)
            else:
                bgOptions = []

                bgOptions.append(miru.SelectOption("Default background", value="default"))

                for i in range(0, 4, 1):
                    if (userData[5] & (1 << i)) >> i:
                        if i == 0:
                            bgOptions.append(miru.SelectOption("Quoter Developer", value="developer"))
                        if i == 1:
                            bgOptions.append(miru.SelectOption("Beta Tester <3", value="beta"))
                        if i == 2:
                            bgOptions.append(miru.SelectOption("Custom background", value="custom"))

                class customisationPage(miru.View):
                    @miru.text_select(
                        placeholder="Select a background",
                        options=bgOptions
                    )
                    async def backgroundSelect(bgSelf, bgSelect: miru.TextSelect, bgCtx: miru.ViewContext):
                        conn = sql.connect(r"cfgs/qtr.db")

                        conn.commit()
                    
                        cur = conn.execute(f"UPDATE settings SET background = \"{bgSelect.values[0]}\" WHERE id = {ctx.author.id}")

                        conn.commit()
                        if bgSelect.values[0] != "custom":
                            await bgCtx.respond("Set your background successfully!", flags=hikari.MessageFlag.EPHEMERAL)
                        elif bgSelect.values[0] == "custom":
                            modal = customBgHandler(title="Custom background")
                            await bgCtx.respond_with_modal(modal)

                view = customisationPage(timeout=30)

                await ctx.respond("Select a background!", flags=hikari.MessageFlag.EPHEMERAL, components=view)

                plugin.d.miru.start_view(view)

                #await view.wait()

                #await bgMessage.edit("This object has timed out.", components=None)
        elif select.values[0] == "danger":
            view = dangerousSettings(timeout=30)

            if not userData[1]:
                view.disable.label = "Unblock processing"
                view.disable.style = hikari.ButtonStyle.PRIMARY

            view.mainSettings = message

            await ctx.respond("This menu contains actions that might stop Quoter from working, please be careful.\nBlock processing ➡️ Prevents your data from being processed by Quoter (other than settings). In layman's terms: it means you can't be quoted.", flags=hikari.MessageFlag.EPHEMERAL, components=view)

            plugin.d.miru.start_view(view)
            #await view.wait()
            #await dangerMsg.edit("This object has timed out.", components=None)
        else:
            await ctx.respond(f"Unknown page??\n{select.values[0]} isn't a valid page, please report this!", flags=hikari.MessageFlag.EPHEMERAL)

@plugin.command()
@lightbulb.command('settings', 'Access your settings to do with Quoter', auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def settings(ctx: lightbulb.SlashContext):
    conn = sql.connect(r"cfgs/qtr.db")

    conn.commit()

    cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.author.id}")

    authorData = cur.fetchall()

    if not authorData:
        global defaultSettings
        _ = conn.execute(defaultSettings, (int(ctx.author.id),))
        conn.commit()
        cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.author.id}")
        authorData = cur.fetchall()
    
    conn.close()
    authorDataTuple = authorData[0]

    view = settingsView()

    frontendUserData = []
    
    for i in authorDataTuple:
            if isinstance(i, int):
                if str(i) == "0":
                    frontendUserData.append("❌")
                elif str(i) == "1":
                    frontendUserData.append("✅")
                else:
                    frontendUserData.append(i)
            else:
                frontendUserData.append(i)

    view.userData = authorDataTuple

    message = await ctx.respond(f"# Welcome to the Quoter settings panel!\nAccount overview:\n- Active account: {frontendUserData[1]}\n- Banned account: {frontendUserData[2]}\n- Background: {frontendUserData[3]}\n- Send a DM when someone quotes you: {frontendUserData[4]}\n- Unlocked backgrounds: `{frontendUserData[5]}`", components=view)
    view.response = message
    ctx.app.d.miru.start_view(view)

    #await view.wait()

    #await message.edit("This settings menu has timed out.", components=None)