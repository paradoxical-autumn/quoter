import lightbulb, os, json, hikari, random, logging
from PIL import Image
from datetime import datetime
import requests
import string
import imagetext_py as imgtxt
import sqlite3 as sql

sql.connect(r"cfgs/qtr.db")

USER_PAIR_OFFSET = 128
QUOTE_SIZE = 96
USER_DEETZ_SIZE = 64
QUOTE_PXLS = 900

plugin = lightbulb.Plugin("qtr_MAIN")

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

@plugin.command()
@lightbulb.add_cooldown(30, 1, qtr_COOLDOWN)
@lightbulb.command('Quote', 'Someone say something that\'s too perfect NOT to quote?', auto_defer=True)
@lightbulb.implements(lightbulb.MessageCommand)
async def quote(ctx: lightbulb.MessageContext):
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
        
    
    cur = conn.execute(f"SELECT * FROM settings WHERE settings.id = {ctx.options.target.author.id}")
    targetData = cur.fetchall()

    if not targetData:
        targetData = [(int(ctx.options.target.author.id), 1, 0, "default", 0, 0, None,)]

    conn.close()
    authorDataTuple = authorData[0]
    targetDataTuple = targetData[0]

    if targetDataTuple[4]:
        guild = ctx.get_guild()
        try:
            await ctx.options.target.author.send(f"# Yikes!\n{ctx.author.username} just quoted you in {guild.name}!\nYou said \"{ctx.options.target.content}\"\n*(You have recieved this alert as you have DM On Quote enabled)*")
        except hikari.ForbiddenError:
            pass

    if authorDataTuple[1] == False or targetDataTuple[1] == False:
        await ctx.respond(hikari.Embed(title=f"Unable to generate quote.", description=f"Either you or {ctx.options.target.author.username} has opted out of quoter.", color=0xFF0000))
        return

    
    if str(ctx.options.target.author.id) == "1034045810993803325":
        await ctx.respond(hikari.Embed(title=random.choice(["😏", "???", "aeiou", "why??", "!", "you just wasted a cooldown!", "good job!"]), description="You can't quote the quoter as the quoter can't be quoted.\n*(you can't quote me and im wondering why you would even do that.)*", color=0xFF6D00))
        return None
    
    
    if authorDataTuple[2] == True:
        await ctx.respond(hikari.Embed(title=f"Banned", description=f"You're banned from using Quoter.", color=0x414141))
        return

    try:
        gradBg = Image.open(r"defaultAssets/grad.png") # main background for every user
        devGradBg = Image.open(r"defaultAssets/MODERN_grad_dev.png") # developer background
        betaGradBg = Image.open(r"defaultAssets/MODERN_grad_beta.png") # beta tester background
    except FileNotFoundError:
        logging.fatal("Gradient not found\nIs it saved in the 'defaultAssets' folder?") # oops we can't load the backgrounds
        raise FileNotFoundError("Gradient not found. Ask the developer to fix this.")

    #global setCtx # THESE TWO LINES ARE USED FOR DEBUGGING.
    #setCtx = ctx # AT EXIT, THESE ARE STORED SO I CAN ANALYSE THEM FOR INFORMATION!!
    #await ctx.respond(f"{ctx.author} -> {ctx.author=}\n\n{ctx.options.target.author} -> {ctx.options.target.author=}\n\n{ctx.options.target=}")

    if ctx.options.target.author.global_name:
        nick = f"{ctx.options.target.author.global_name}"
    else:
        nick = None
    
    username = f"@{ctx.options.target.author.username}"

    logging.debug("username ok!")
    
    try:
        quotestr = ctx.options.target.content # get the quote
        if quotestr:
            logging.debug("qtstr ok!")
        else:
            raise ValueError
    except:
        await ctx.respond(hikari.Embed(title="Message content not found", description="Either:\n- You tried to quote a message with no text content\n- You tried to quote a message where the text was in an embed", color=0xFFFF00)) # oops we can't find the quote
        return

    try:
        avatar = Image.open(requests.get(f"{ctx.options.target.author.avatar_url}", stream=True).raw) # get the user's avatar
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

    if targetDataTuple[3] == "default":
        layer2 = gradBg
    elif targetDataTuple[3] == "beta":
        layer2 = betaGradBg
    elif targetDataTuple[3] == "developer":
        layer2 = devGradBg
    elif targetDataTuple[3] == "custom" and targetDataTuple[6] != None:
        try:
            layer2 = Image.open(requests.get(f"{targetDataTuple[6]}", stream=True).raw)
            layer2 = layer2.resize((1920, 1080))
            layer2 = layer2.convert("RGBA")
        except Exception as err:
            try:
                await ctx.options.target.author.send("# error\nyour custom background isn't formatted right lmao. you're gonna get dms like this until you change it.\ncustom backgrounds:\n- SHOULD be 1920 by 1080px but will be resized\n- SHOULD have a transparent region between (0, 0) and (1080, 1080) else your avatar wont show up\n- should be dark theme as quote text is white\n\nand finally\n- **be a direct link to an image file, try using \"Copy Link\" after uploading and right clicking on an image uploaded to Discord.**\n\nhere's a link to a [GUIDE](<https://media.discordapp.net/attachments/1139436636808163350/1154823484896190495/image.png>) on how to make custom quotes and here's the [default background](<https://media.discordapp.net/attachments/1139436636808163350/1154823519666974770/grad.png>)")
            except hikari.ForbiddenError:
                pass
            layer2 = gradBg
    else:
        layer2 = gradBg

    final1 = Image.new("RGBA", layer2.size)
    final1.paste(layer1, (0,0))
    final1.paste(layer2, (0,0))

    avatarCanvas = Image.new("RGBA", layer2.size)
    avatarCanvas.paste(avatarRS)

    final2 = Image.new("RGBA", layer2.size)
    final2 = Image.alpha_composite(final2, avatarCanvas)
    final2 = Image.alpha_composite(final2, layer2)

    # save it as "final.png"
    # if we're on windows, save it to %tmp%/quoter_bot
    # else, save it to that weird "outputs" directory

    qtid = ""
    for _ in range(16):
        qtid += random.choice(string.ascii_letters)

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

    for i in ctx.options.target.user_mentions:
        quotestr = quotestr.replace(ctx.options.target.user_mentions[i].mention, f"@{ctx.options.target.user_mentions[i].username}")

    # load font.
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

    greyed = final2WITHAddedQuote.convert()

    # if we're on windows, save it to %tmp%/quoter_bot
    # else, save it to outputs.
    ratioMessage = random.choice(qtRatios)
    ratioMessage = ratioMessage.replace("<atk>", ctx.author.mention)
    ratioMessage = ratioMessage.replace("<def>", ctx.options.target.author.mention)
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
