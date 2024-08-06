import lightbulb, logging, hikari
import sqlite3 as sql

plugin = lightbulb.Plugin("sql", include_datastore=True)

def load(bot: lightbulb.BotApp):
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

@plugin.listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):
    if event.is_human and event.content:
        me = plugin.bot.get_me()

        if str(event.author_id) != "730089700139991060":
            return
        
        if not event.content.startswith(f"{me.mention} sql"): # i wish i could just use an exclamation mark here.
            return
        
        conn = sql.connect(r"cfgs/qtr.db")
        conn.commit()

        cur = conn.execute(event.content.strip(f"{me.mention} sql "))
        data = cur.fetchall()
        if len(data) == 0:
            await event.message.respond(f"-> `{event.content.strip(f'{me.mention} sql ')}`\n*No database response.*")
        else:
            await event.message.respond(f"-> `{event.content.strip(f'{me.mention} sql ')}`\n{data}")
        
        conn.commit()
        conn.close()