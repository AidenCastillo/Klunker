# klunker
Discord py bot that can play magic the gathering

# Using
A few things you may like/need to know before using this bot.

## Setup
First thing you need to do before using klunker is create a `variable.py` file in the same directory as main.py. All items found in the section `Variables` will be placed into the `variable.py` file formated as:

* `variable = ""` for string variables, stated in the following section.
* `int = 123` for integer variables, stated in the following section.
* `bool = True/False` for boolean variables, stated in the following section.

### Variables
* `Token` **String** - This is a required variable, you must put your discord bot token found at discord.com/developers.
* `testmode` **Boolean** - This is a required variable, enables testing features, bypasses some checks, and enabeles beta/upcoming features.
* `ownerID` **Integer** - This may be a required variable for some commands. Place the owner of the bot's `Discord ID`

## Customizable Parts
Most of the files in `data/` are customizable to your own needs. If you decide to add something to those files or edit the json files, we recommend to keep the same formate as the previous items in the files.
