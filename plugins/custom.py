import lightbulb, os, json, hikari, random, logging
from PIL import Image
from datetime import datetime
import requests
import string
import imagetext_py as imgtxt
import sqlite3 as sql

USER_PAIR_OFFSET = 128
QUOTE_SIZE = 96
USER_DEETZ_SIZE = 64
QUOTE_PXLS = 900

plugin = lightbulb.Plugin("qtr_CUSTOM")

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

@plugin.command
@lightbulb.add_cooldown(30, 1, qtr_COOLDOWN)
@lightbulb.option("text", "What did they say?", hikari.OptionType.STRING, required=True)
@lightbulb.option("user", "Who are you quoting?", hikari.OptionType.USER, required=True)
@lightbulb.command('custom', 'Create a fake quote of someone.', auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def unofficial(ctx: lightbulb.MessageContext):
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
        
        try:
            await ctx.author.send(f"# Welcome to Quoter, {ctx.author.mention}!\n*Your data has been set up/ported over to the new V3 API.*\nYou can access settings by running /settings!\n\nHave a fun time using Quoter!")
        except hikari.ForbiddenError:
            pass
    
    cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.options.user.id}")
    targetData = cur.fetchall()

    if not targetData:
        targetData = [(int(ctx.options.user.id), 1, 0, "default", 0, 0, None,)]

    conn.close()
    authorDataTuple = authorData[0]
    targetDataTuple = targetData[0]

    if targetDataTuple[4]:
        guild = ctx.get_guild()
        await ctx.options.user.send(f"# Yikes!\n{ctx.author.username} just custom quoted you in {guild.name}!\nApparently you said \"{ctx.options.text}\"\n*(You have recieved this alert as you have DM On Quote enabled)*")

    if authorDataTuple[1] == False or targetDataTuple[1] == False:
        await ctx.respond(hikari.Embed(title=f"Unable to generate quote.", description=f"Either you or {ctx.options.user.username} has opted out of quoter.", color=0xFF0000))
        return
    
    if ctx.options.user.is_bot:
        await ctx.respond(hikari.Embed(title=random.choice(["😏", "???", "aeiou", "why??", "!", "you just wasted a cooldown!", "good job!"]), description="Bots cannot be quoted", color=0xFF6D00))
        return None
    
    if authorDataTuple[2] == True:
        await ctx.respond(hikari.Embed(title=f"Banned", description=f"You're banned from using Quoter.", color=0x414141))
        return

    # Main, April Fools and developer backgrounds
    try:
        if ctx.author.id != ctx.options.user.id:
            gradBg = Image.open(r"defaultAssets/unofficial.png") # main background for every user
        else:
            gradBg = Image.open(r"defaultAssets/grad.png")
    except FileNotFoundError:
        logging.fatal("Gradient not found\nIs it saved in the 'defaultAssets' folder?") # oops we can't load the backgrounds
        raise FileNotFoundError("Gradient not found. Ask the developer to fix this.")

    #global setCtx # THESE TWO LINES ARE USED FOR DEBUGGING.
    #setCtx = ctx # AT EXIT, THESE ARE STORED SO I CAN ANALYSE THEM FOR INFORMATION!!
    #await ctx.respond(f"{ctx.author} -> {ctx.author=}\n\n{ctx.options.target.author} -> {ctx.options.target.author=}\n\n{ctx.options.target=}")


    #if ctx.options.user.global_name:
    #    username = f"{ctx.options.user.global_name}"
    #else:
    #    username = f"@{ctx.options.user.username}" # get the username

    if ctx.options.user.global_name:
        nick = f"{ctx.options.user.global_name}"
    else:
        nick = None
    
    username = f"@{ctx.options.user.username}" # get the username

    logging.debug("username ok!")

    try:
        quotestr = ctx.options.text # get the quote
        if quotestr:
            logging.debug("qtstr ok!")
        else:
            raise ValueError
    except:
        await ctx.respond("that message has no content!") # oops we can't find the quote
        return
    
    try:
        avatar = Image.open(requests.get(f"{ctx.options.user.avatar_url}", stream=True).raw) # get the user's avatar
        logging.debug("avatar ok!")
    except:
        # hikari.User.default_avatar_url
        avatar = Image.open(requests.get("https://cdn.discordapp.com/embed/avatars/0.png", stream=True).raw) # okay so they don't have one
        logging.warning("default avatar lol.")
    
    #for i in cleanedBannedWords:
    #    quotestr = quotestr.replace(i, "*")
    
    logging.debug("MOVING ONTO GENERATION")

    # create basic graphic.
    # that's the avatar and background.
    avatarCpy = avatar.copy()
    avatarRS = avatarCpy.resize((1080, 1080))
    layer1 = avatarRS
    layer2 = gradBg
    final1 = Image.new("RGBA", layer2.size)
    final1.paste(layer1, (0,0))
    final1.paste(layer2, (0,0))

    avatarCanvas = Image.new("RGBA", layer2.size)
    avatarCanvas.paste(avatarRS)

    final2 = Image.new("RGBA", layer2.size)
    final2 = Image.alpha_composite(final2, avatarCanvas)
    final2 = Image.alpha_composite(final2, layer2)

    # generate the file to be uploaded.
    # we randomise the file name.
    qtid = ""

    for _ in range(16):
        qtid += random.choice(string.ascii_letters)

    # save it as "final.png"
    # if we're on windows, save it to %tmp%/quoter_bot
    # else, save it to that weird "outputs" directory
    if notWindows == False:
        if not os.path.isdir(rf"{os.environ['tmp']}/quoter_bot"):
            os.mkdir(rf"{os.environ['tmp']}/quoter_bot")

        final2.save(rf"{os.environ['tmp']}/quoter_bot/final_{qtid}.png")
    else:
        if not os.path.isdir("outputs"):
            logging.warning("creating outputs folder")
            os.mkdir("outputs")
        
        final2.save(rf"outputs/final_{qtid}.png")

    # create a copy of the background.
    final2WithoutAddedQuote = final2.copy()

    # create a new drawing canvas, with the size of the background
    drawingCanvas = Image.new("RGBA", final2.size)

    # load fonts.
    imgtxt.FontDB.SetDefaultEmojiOptions(imgtxt.EmojiOptions(parse_discord_emojis=True, source=imgtxt.EmojiSource.Twemoji))
    quoterFont = imgtxt.FontDB.Query("NotoSans-Regular NotoSansJP-Regular NotoSansSC-Regular NotoSansTC-Regular NotoSansHK-Regular NotoSansKR-Regular")
    #\n~ {nick}, {ctx.options.target.timestamp.strftime('%Y')}"
    wrapped_qtr = imgtxt.text_wrap(f"{quotestr}", QUOTE_PXLS, QUOTE_SIZE, quoterFont, True, imgtxt.WrapStyle.Word)

    with drawingCanvas as im:
        with imgtxt.Writer(im) as w:
            _, nickOffset = imgtxt.text_size_multiline(wrapped_qtr, QUOTE_SIZE, quoterFont, 1, True)

            w.draw_text_wrapped(
                text=quotestr,
                x=1000, y=540,
                ax=0, ay=0.5,
                width=QUOTE_PXLS,
                size=QUOTE_SIZE,
                font=quoterFont,
                fill=imgtxt.Paint.Color((255, 255, 255, 255)),
                align=imgtxt.TextAlign.Center,
                draw_emojis=True
                )

            if nick:
                _, usrOffset = imgtxt.text_size(nick, USER_DEETZ_SIZE, quoterFont, True)
            else:
                usrOffset = 0

            if nick:
                w.draw_text_wrapped(
                    text=f"~ {nick}",
                    x=1000, y=540 + USER_PAIR_OFFSET + (nickOffset/2),
                    ax=0, ay=0.5,
                    width=QUOTE_PXLS,
                    size=USER_DEETZ_SIZE,
                    font=quoterFont,
                    fill=imgtxt.Paint.Color((255, 255, 255, 255)),
                    align=imgtxt.TextAlign.Center,
                    draw_emojis=True
                    )

                w.draw_text_wrapped(
                    text=f"{username}",
                    x=1000, y=540 + USER_PAIR_OFFSET + (nickOffset/2) + usrOffset,
                    ax=0, ay=0.5,
                    width=QUOTE_PXLS,
                    size=USER_DEETZ_SIZE,
                    font=quoterFont,
                    fill=imgtxt.Paint.Color((128, 128, 128, 255)),
                    align=imgtxt.TextAlign.Center,
                    draw_emojis=True
                    )
            else:
                w.draw_text_wrapped(
                    text=f"~ {username}",
                    x=1000, y=540 + USER_PAIR_OFFSET + (nickOffset/2) + usrOffset,
                    ax=0, ay=0.5,
                    width=QUOTE_PXLS,
                    size=USER_DEETZ_SIZE,
                    font=quoterFont,
                    fill=imgtxt.Paint.Color((255, 255, 255, 255)),
                    align=imgtxt.TextAlign.Center,
                    draw_emojis=True
                    )

    #final2WithoutAddedQuote.paste(drawingCanvas)
    #
    #final2WithoutAddedQuote.show()

    # paste the background with quote added on top into one image.
    final2WITHAddedQuote = Image.alpha_composite(final2WithoutAddedQuote, drawingCanvas)

    # keep it coloured.
    greyed = final2WITHAddedQuote.convert()
    #greyed.show()

    # if we're on windows, save it to %tmp%/quoter_bot
    # else, save it to outputs.
    ratioMessage = random.choice(qtRatios)
    ratioMessage = ratioMessage.replace("<atk>", ctx.author.mention)
    ratioMessage = ratioMessage.replace("<def>", ctx.options.user.mention)
    if notWindows == False:
        greyed.save(rf"{os.environ['tmp']}/quoter_bot/{qtid}.png")

        # upload the file
        await ctx.respond(content=ratioMessage, attachment=hikari.File(rf"{os.environ['tmp']}/quoter_bot/{qtid}.png"))

        # delete the file once we're done.
        # this is both for privacy reasons and to save disk space.
        os.remove(rf"{os.environ['tmp']}/quoter_bot/{qtid}.png")
        os.remove(rf"{os.environ['tmp']}/quoter_bot/final_{qtid}.png")
    else:
        greyed.save(rf"outputs/{qtid}.png")

        # upload the file
        await ctx.respond(content=ratioMessage, attachment=hikari.File(rf"outputs/{qtid}.png"))

        # delete the file once we're done.
        # this is both for privacy reasons and to save disk space.
        os.remove(rf"outputs/{qtid}.png")
        os.remove(rf"outputs/final_{qtid}.png")