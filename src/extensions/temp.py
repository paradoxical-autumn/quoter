import lightbulb, logging

plugin = lightbulb.Plugin("qtr_TMP", include_datastore=True)

def load(bot: lightbulb.BotApp):
    print("yo we're installed!!")
    try:
        bot.add_plugin(plugin)
    except lightbulb.CommandAlreadyExists as err:
        logging.error(err)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)