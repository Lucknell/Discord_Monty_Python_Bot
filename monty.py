import os
import discord
import configparser
import logging
from datetime import datetime
from discord.ext import commands
from discord.ext import tasks

Bot_Name = "Monty Python"

client = commands.Bot(command_prefix=commands.when_mentioned_or('$'))
client.remove_command('help')  # remove the default help message

config = configparser.ConfigParser()
config.read('config.ini')

avatar_path = "/src/bot/avatar.png"
fp = open(avatar_path, 'rb')
avatar = fp.read()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)  # Do not allow DEBUG messages through
handler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter(
    "{asctime}: {levelname}: {name}: {message}", style="{"))
logger.addHandler(handler)

helpMessage = discord.Embed(
    title="Help message and the quest for the holy grail",
    color=discord.Color(0xff94aa),
    timestamp=datetime.now()
)

helpMessage.set_footer(text="plz send help I have been on since")
helpMessage.add_field(
    name="commands", value="$dc\n$status\n$game\n$joke\n$fact\n$totext URL of an image\n$wiki topic\n$wiki_info topic\n $poll\n$count\n$pokemon igglybuff\n$reaction\n$lyrics")
helpMessage.add_field(name="voice chat commands",
                      value="$say something\n$parler omelette au fromage\n$hablar tengo un gato en mis pantalones\n\
                          $skazat медведь на одноколесном велосипеде\n$dire something italian\n$zip 33016\n$sing song name\n$canta song name")
helpMessage.add_field(
    name="Games", value="I wish to cross the bridge of death\nMad Minute\nGame show\ntic-tac-toe\nFermi\n")


@client.event
async def on_ready():
    print('And the holy grail')
    try:
        await client.user.edit(avatar=avatar)
    except discord.errors.HTTPException:
        pass
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Holy Grail"))


@client.command()
async def help(ctx):
    await ctx.send(embed=helpMessage)

files = os.listdir("/src/bot/cogs/")
for f in files:
    if f.endswith(".py"):
        client.load_extension("cogs." + f.replace(".py", ""))

client.run(config['bot-token']['token'])
