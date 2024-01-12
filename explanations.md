<h1 align="center">explanations</h1>
<p align="center">aka the "what does each file do" page.</p>

# src/main.py
simply runs the bot itself and registers devtools.

# src/cfgs
this folder holds all the possible configs you could want for the bot. it also holds the database so be careful with that.

| file              | explanation                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- |
| defaultData       | holds the SQL command for creating user data and assigning temporary data                   |
| feedbackBans.json | <legacy file> holds all the user IDs of users banned from posting feedback, no longer used. |
| messages.json     | holds all the possible status messages using a custom format.                               |
| qtMsgs.json       | holds all the messages that appear when someone gets quoted.                                |
| tr.db             | the main database file (SQLite3), don't touch.                                              |
| ranks.json        | which users are allowed to access what permissions? currently only holds devtools.          |

# src/defaultAssets
holds all the graphics used by the bot

# src/extensions
<unused>

# src/outputs
holds all quotes that are currently being generated.

# src/plugins
holds the individual components of quoter due to its modular nature

| file            | explanation                                                   |
| --------------- | ------------------------------------------------------------- |
| \_\_init\_\_.py | required by python to load files                              |
| custom.py       | holds the code for custom quotes                              |
| quote.py        | holds the code for quotes                                     |
| sd.py           | holds the code allowing the bot to self destruct. long story. |
| settings.py     | holds the code for the user settings                          |

# src/unused_plugins
unused components