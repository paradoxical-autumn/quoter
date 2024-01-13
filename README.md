<h1 align="center">Quoter</h1>
<p align="center"><i>a stupid discord bot.</i></p>

## About
Quoter is a Discord bot that allows for users to make visual quotes out of images, similar to those you can get by searching for "motivational quotes" on the internet.

## A comment about this bot
I'd prefer it if you just added [my version](https://discord.com/oauth2/authorize?client_id=1034045810993803325&permissions=274877959168&scope=applications.commands%20bot) of the bot to your servers, but if it goes down or if you just REALLLYYYY want a self hosted instance, I've released this code for ya.

Nevertheless...
## Running
1. **Downloading the code**

Meet my old friend, `git clone`. Seriously, that's it.

2. **Set up python**

Quoter currently runs Python `3.11.3` on a GNU/Linux webserver, but future versions of python and a windows PC should work too.

3. (Optional) **Set up a venv**

*(So the packages don't interfere with your other projects)*
Run `python3 -m venv venv`. if you're using windows it's probably `python` and not `python3`

4. **Install the requirements**

Just run `pip install -U -r requirements.txt`

5. **Run the bot client**

We don't need to compile it. The command I use to run it is `python3 -OO main.py`
*(the `-OO` flag does some optimisation)*

## disclaimer
this code is an absolute mess as ive been working on it for years and never deleted unused features, just commented them out.

also, since it was only me working on it, i didn't add many comments.