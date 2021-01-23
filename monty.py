import os
import discord
import pyttsx3
import time
import asyncio
import requests
import random
import shutil
import configparser
import pytesseract
import re
import logging
from wikipedia import wikipedia
from lyrics import lyric_finder, SongNotFoundError
from quote import quote_finder, InvalidCategoryGiven, QuoteNotFoundError
import numpy as np
from datetime import datetime
from PIL import Image
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
    name="commands", value="$dc\n$status\n$game\n$joke\n$fact\n$totext URL of an image\n")
helpMessage.add_field(name="voice chat commands",
                      value="$say something\n$parler omelette au fromage\n$hablar tengo un gato en mis pantalones\n\
                          $skazat медведь на одноколесном велосипеде\n$dire something italian\n$zip 33016\n$sing song name\n$canta song name")
helpMessage.add_field(
    name="Games", value="I wish to cross the bridge of death\nMad Minute\nGame show\ntic-tac-toe\n")
queue = {}


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


@client.command()
async def say(ctx):
    await TTStime(ctx, "say", 17)


@client.command()
async def skazat(ctx):
    await TTStime(ctx, "skazat", 54)


@client.command()
async def hablar(ctx):
    await TTStime(ctx, "hablar", 18)


@client.command()
async def parler(ctx):
    await TTStime(ctx, "parler", 24)


@client.command()
async def dire(ctx):
    await TTStime(ctx, "dire", 34)


@client.command()
async def hanasu(ctx):
    await TTStime(ctx, "hanasu", 39)


@client.command(aliases=['jouer'])
async def game(ctx):
    await ctx.send("What do you want to do " + (ctx.author.nick if ctx.author.nick != None else ctx.author.name) + "?")
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        return await ctx.send("https://tenor.com/view/game-over-insert-coins-gif-12235828")
    if msg.content.lower() == "i wish to cross the bridge of death":
        await bridge_of_death(ctx)
    elif msg.content.lower() == "mad minute":
        await mad_minute(ctx)
    elif msg.content.lower() == "game show":
        await game_show(ctx)
    elif msg.content.lower() == "tic tac toe" or msg.content.lower() == "tic-tac-toe":
        await tic_tac_toe(ctx)
    else:
        return await ctx.send("You what? Get some $help")


@client.command(aliases=['disconnect', 'leave'])
async def dc(ctx):
    if ctx.message.author.voice.channel:
        serverQueue = queue.get(ctx.message.guild.id)
        if serverQueue == None:
            return
        await serverQueue.connection.disconnect()
        queue.pop(ctx.message.guild.id)


@client.command()
@commands.has_role('Monty\'s keeper')
async def skip(ctx):
    if not ctx.message.author.voice.channel:
        return
    serverQueue = queue.get(ctx.message.guild.id)
    if serverQueue == None:
        return
    serverQueue.connection.stop()


@client.command()
async def status(ctx):
    statuses = ["Jokes on you we still alive", "I'm fine, get X go", "Systems online awaiting next task",
                "Damage report returned. No damage found", "You scared ain't ya?"]
    # randInt is inclusive of the upper bound
    return await ctx.send(statuses[random.randint(0, len(statuses) - 1)])


@client.command()
async def zip(ctx, arg=None):
    error_cases = ["https://tenor.com/view/family-guy-ollie-williams-its-raining-side-ways-weatherman-weather-gif-5043009",
                   "https://tenor.com/view/rain-its-gon-rain-weather-report-gif-5516318"]
    # await client.user.edit(username=names[random.randint(0, len(names) - 1)])
    if not arg:
        return await ctx.send(error_cases[random.randint(0, len(error_cases) - 1)])
    API_key = config['openweathermap']['api_key']
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    Final_url = base_url + "appid=" + API_key + "&zip=" + arg
    weather_data = requests.get(Final_url).json()
    # print(weather_data)
    if weather_data["cod"] == "404":
        # await client.user.edit(username=Bot_Name)
        return await ctx.send("invalid zipcode")
    #enhanced_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&appid={}"
    #exclude = "minutely,hourly,daily"
    # enhanced_weather_data = requests.get(enhanced_url.format(
    # weather_data["coord"]["lat"], weather_data["coord"]["lon"], exclude, API_key)).json()
    # print(enhanced_weather_data)
    temp = str(round(KtoF(weather_data["main"]["temp"]), 1))
    feels_like = str(round(KtoF(weather_data["main"]["feels_like"]), 1))
    temp_min = str(round(KtoF(weather_data["main"]["temp_min"]), 1))
    temp_max = str(round(KtoF(weather_data["main"]["temp_max"]), 1))
    humidity = str(weather_data["main"]["humidity"])
    wind_speed = str(weather_data["wind"]["speed"])
    wind_dir = wind_degree(weather_data["wind"]["deg"])
    #wind_gust = str(weather_data["wind"]["gust"])
    weather_talk = "Currently the weather for {} is, {} with {}, the temperature is {} degrees Fahrenheit. \
It currently feels like {} degrees Fahrenheit. The low and high are {} and {}. The humidity is at \
{}% with a wind speed of {} mph moving {}. Have a good day {}"
    weather_talk = weather_talk.format(weather_data["name"], weather_data["weather"][0]["main"],
                                       weather_data["weather"][0]["description"], temp, feels_like, temp_min, temp_max,
                                       humidity, wind_speed, wind_dir, (ctx.message.author.nick if ctx.message.author.nick != None else ctx.message.author.name))
    if ctx.message.author.voice:
        await TTStime(ctx, "", 14, say=weather_talk, rate=125)
    else:
        await ctx.send(weather_talk)
    # await client.user.edit(username=Bot_Name)


@client.command()
async def joke(ctx):
    headers = {"Accept": "application/json"}
    url = "https://icanhazdadjoke.com/"
    joke_data = requests.get(url, headers=headers).json()
    await ctx.send(joke_data["joke"])
    if ctx.message.author.voice:
        await TTStime(ctx, "", 17, joke_data["joke"])


@client.command()
async def fact(ctx):
    headers = {"Accept": "application/json"}
    url = "https://useless-facts.sameerkumar.website/api"
    fact_data = requests.get(url, headers=headers).json()
    await ctx.send(fact_data["data"])


@client.command()
async def totext(ctx, arg=None):
    if not arg:
        return await ctx.send("Try that again but give me a URL to an image next time")
    url = valid_URL(arg)
    if not url:
        return await ctx.send("invalid URL")
    url = url.string
    filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    try:
        img = np.array(Image.open(filename))
    except Image.UnidentifiedImageError:
        os.remove(filename)
        return await ctx.send("Not an image")
    text = pytesseract.image_to_string(img)
    os.remove(filename)
    await ctx.send(text)


@client.command()
async def good(ctx, arg):
    if arg.lower() == "bot":
        await ctx.message.add_reaction("😄")


@client.command()
async def bad(ctx, arg):
    if arg.lower() == "bot":
        await ctx.send("alright then.")


@client.command()
async def sing(ctx, *, args):
    await __sing(ctx, args, 17)


@client.command()
async def canta(ctx, *, args):
    await __sing(ctx, args, 18)


async def __sing(ctx, args, lang):
    # return await ctx.send("This function is disabled")
    try:
        song = lyric_finder(args)
    except SongNotFoundError:
        return await ctx.send("Song could not be found")
    await ctx.send("Sing along here\n{}".format(song.URL))
    for i in range(0, 2, 1):
        await TTStime(ctx, "", lang, song.lyric_array[i], name=str(random.randint(0, 10000)))


@client.command()
async def wiki(ctx, *, args):
    wiki = wikipedia(args)
    try:
        return await ctx.send("{} \nRead more here: {}".format(wiki.summary, wiki.url))
    except AttributeError:
        return await ctx.send("No articles found")


@client.command()
async def quote(ctx, category, *, search=None):
    try:
        quote = quote_finder(category, search)
    except QuoteNotFoundError:
        return await ctx.send("No quotes found")
    except InvalidCategoryGiven:
        return await ctx.send("get some $help you gave an invalid category.")
    if len(quote.quote) > 2000:
        await ctx.send(quote.quote[0:2000])
        return await ctx.send(quote.quote_URL)
    else:
        return await ctx.send("{}\n{}".format(quote.quote, quote.quote_URL))


@client.command()
async def about(ctx):
    return await ctx.send("You can learn more about me here\nhttps://github.com/Lucknell/Discord_Monty_Python_Bot")

def wind_degree(int):
    if (int > 345 and int < 361) or (int > -1 and int < 16):
        return "N"
    elif int > 15 and int < 36:
        return "N/NE"
    elif int > 35 and int < 56:
        return "NE"
    elif int > 55 and int < 76:
        return "E/NE"
    elif int > 75 and int < 106:
        return "E"
    elif int > 105 and int < 126:
        return "E/SE"
    elif int > 125 and int < 146:
        return "SE"
    elif int > 145 and int < 166:
        return "S/SE"
    elif int > 165 and int < 196:
        return "S"
    elif int > 195 and int < 216:
        return "S/SW"
    elif int > 215 and int < 236:
        return "SW"
    elif int > 235 and int < 256:
        return "W/SW"
    elif int > 255 and int < 286:
        return "W"
    elif int > 295 and int < 306:
        return "W/NW"
    elif int > 305 and int < 326:
        return "NW"
    elif int > 325 and int < 346:
        return "N/NW"
    else:
        return "You really shouldn't be seeing this..."


def valid_URL(str):
    return re.search(r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$", str)


async def tic_tac_toe(ctx):
    await ctx.send("This is an beta test")
    await ctx.send("What difficulty?\nEasy\nHard")
    difficulty = "easy"
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        await ctx.send("You had one job.")
        return await ctx.send("https://tenor.com/view/south-park-fractured-difficulty-gif-10182175")
    if msg.content.lower() == "hard" or msg.content.lower() == "h":
        difficulty = "hard"
    message = await ctx.send("Loading...")
    await message.add_reaction("0️⃣")
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")
    await message.add_reaction("5️⃣")
    await message.add_reaction("6️⃣")
    await message.add_reaction("7️⃣")
    await message.add_reaction("8️⃣")
    board = "0️⃣1️⃣2️⃣\n3️⃣4️⃣5️⃣\n6️⃣7️⃣8️⃣"
    vboard = ["c", "c", "c", "c", "c", "c", "c", "c", "c"]
    current = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
    await message.edit(content=board)
    ticker = await ctx.send("Your move")

    def check_reaction(user):
        def inner_check(reaction, author):
            return user == author and str(reaction.emoji) in current
        return inner_check

    def check_winner(member):
        if vboard[0] != "c" and vboard[0] == vboard[1] and vboard[1] == vboard[2]:
            if vboard[0] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[3] != "c" and vboard[3] == vboard[4] and vboard[4] == vboard[5]:
            if vboard[3] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[6] != "c" and vboard[6] == vboard[7] and vboard[7] == vboard[8]:
            if vboard[0] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[0] != "c" and vboard[0] == vboard[3] and vboard[3] == vboard[6]:
            if vboard[0] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[1] != "c" and vboard[1] == vboard[4] and vboard[4] == vboard[7]:
            if vboard[1] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[2] != "c" and vboard[2] == vboard[5] and vboard[5] == vboard[8]:
            if vboard[2] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[0] != "c" and vboard[0] == vboard[4] and vboard[4] == vboard[8]:
            if vboard[0] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        elif vboard[2] != "c" and vboard[2] == vboard[4] and vboard[4] == vboard[6]:
            if vboard[2] == "x":
                return (member.nick if member.nick != None else member.name) + " Wins!"
            else:
                return "I win!"
        else:
            return None

    while len(current) != 0:
        await ticker.edit(content="Your move")
        try:
            # returns a tuple with a reaction and member object
            reaction, member = await client.wait_for('reaction_add', timeout=30, check=check_reaction(ctx.author))
        except asyncio.TimeoutError:
            return await ticker.edit(content="Game over")
        await ticker.edit(content="Nice choice!")
        if not str(reaction.emoji) in current:
            return await ctx.send("wait that was illegal")
        current.remove(reaction.emoji)
        board = board.replace(reaction.emoji, "❌")
        num = int(reaction.emoji[0])
        vboard[num] = "x"
        await message.edit(content=board)
        win = check_winner(member)
        if win:
            return await ticker.edit(content=win)
        if len(current) == 0:
            return await ticker.edit(content="Games over")
        await ticker.edit(content="My move")
        if difficulty == "hard":
            if vboard[4] == "c":
                choice = current.index("4️⃣")
            elif vboard[0] == "x" and vboard[0] == vboard[1] and vboard[2] == "c":
                choice = current.index("2️⃣")
            elif vboard[1] == "x" and vboard[1] == vboard[2] and vboard[0] == "c":
                choice = current.index("0️⃣")
            elif vboard[2] == "x" and vboard[2] == vboard[0] and vboard[1] == "c":
                choice = current.index("1️⃣")
            elif vboard[3] == "x" and vboard[3] == vboard[4] and vboard[5] == "c":
                choice = current.index("5️⃣")
            elif vboard[4] == "x" and vboard[4] == vboard[5] and vboard[3] == "c":
                choice = current.index("3️⃣")
            elif vboard[5] == "x" and vboard[5] == vboard[3] and vboard[4] == "c":
                choice = current.index("4️⃣")
            elif vboard[6] == "x" and vboard[6] == vboard[7] and vboard[8] == "c":
                choice = current.index("8️⃣")
            elif vboard[7] == "x" and vboard[7] == vboard[8] and vboard[6] == "c":
                choice = current.index("6️⃣")
            elif vboard[8] == "x" and vboard[8] == vboard[6] and vboard[7] == "c":
                choice = current.index("7️⃣")
            elif vboard[0] == "x" and vboard[0] == vboard[6] and vboard[3] == "c":
                choice = current.index("3️⃣")
            elif vboard[0] == "x" and vboard[0] == vboard[3] and vboard[6] == "c":
                choice = current.index("6️⃣")
            elif vboard[3] == "x" and vboard[3] == vboard[6] and vboard[0] == "c":
                choice = current.index("0️⃣")
            elif vboard[1] == "x" and vboard[1] == vboard[7] and vboard[4] == "c":
                choice = current.index("4️⃣")
            elif vboard[1] == "x" and vboard[1] == vboard[4] and vboard[7] == "c":
                choice = current.index("7️⃣")
            elif vboard[4] == "x" and vboard[4] == vboard[7] and vboard[1] == "c":
                choice = current.index("1️⃣")
            elif vboard[2] == "x" and vboard[2] == vboard[8] and vboard[5] == "c":
                choice = current.index("5️⃣")
            elif vboard[2] == "x" and vboard[2] == vboard[5] and vboard[8] == "c":
                choice = current.index("8️⃣")
            elif vboard[5] == "x" and vboard[5] == vboard[8] and vboard[2] == "c":
                choice = current.index("2️⃣")
            elif vboard[4] == "x" and vboard[4] == vboard[0] and vboard[8] == "c":
                choice = current.index("8️⃣")
            elif vboard[4] == "x" and vboard[4] == vboard[2] and vboard[6] == "c":
                choice = current.index("6️⃣")
            elif vboard[4] == "x" and vboard[4] == vboard[8] and vboard[0] == "c":
                choice = current.index("0️⃣")
            elif vboard[4] == "x" and vboard[4] == vboard[6] and vboard[2] == "c":
                choice = current.index("2️⃣")
            else:
                choice = random.randint(0, len(current) - 1)
        else:
            choice = random.randint(0, len(current) - 1)
        board = board.replace(current[choice], "⭕")
        num = int(current[choice][0])
        vboard[num] = "o"
        current.remove(current[choice])
        win = check_winner(member)
        await message.edit(content=board)
        if win:
            return await ticker.edit(content=win)


async def game_show(ctx):
    rounds = 3
    await ctx.send("So who is playing?")
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        return await ctx.send("No one? Got it.")
    players = msg.content.split(" ")
    confirmed_players = []
    confirmed_players.append(GameShow(ctx.author))
    for player in players:
        try:
            member = await msg.guild.fetch_member(int(player.replace("<", "").replace(">", "").replace("@", "").replace("!", "")))
        except discord.errors.NotFound:
            continue
        except discord.errors.HTTPException:
            continue
        except ValueError:
            continue
        # for cplayer in confirmed_players:
        #    if member == cplayer.member:
        #       yield cplayer
        result = [
            cplayer for cplayer in confirmed_players if member == cplayer.member]
        if result:
            continue
        await ctx.send("Do you wish to play " + (member.nick if member.nick != None else member.name) + "?")
        try:
            msg = await client.wait_for('message', check=check(member), timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("No response? Fine then.")
            continue
        if msg.content.lower() == "yes":
            await ctx.send("Welcome aboard")
            confirmed_players.append(GameShow(member))
        else:
            await ctx.send("Someone is chicken")
    await ctx.send("How many rounds?")
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        await ctx.send("No response? Then we will do " + str(rounds) + " rounds")
    if is_int(msg.content):
        rounds = int(msg.content)
        if (rounds * len(confirmed_players)) > 50:
            await ctx.send("Too many rounds given a max of 50 questions will be given.")
            rounds = 50 // len(confirmed_players)
    await ctx.send("That appears to be everyone but lets list them here")
    names = ""
    for player in confirmed_players:
        names += (player.member.nick if player.member.nick !=
                  None else player.member.name)
        names += "\n"
    await ctx.send(names + "\nMay the odds be ever in your favor\nto quit say the following\n**I wish to quit**")
    q_number = rounds * len(confirmed_players)
    url = "https://opentdb.com/api.php?amount=" + str(q_number)
    try:
        api_QA = requests.get(url).json()
    except requests.exceptions.RequestException as e:
        return await ctx.send("I have a bug. Tell my creator\n", e)
    j = 0
    quitting = False
    while j < q_number and not quitting:
        for player in confirmed_players:
            question = ""
            if player.quitting:
                j += 1
                continue
            try:
                if api_QA["results"][j]["type"] == "boolean":
                    question += "True or False?\n"
                question += decodeHTMLSymbols(api_QA["results"][j]["question"])
                if api_QA["results"][j]["type"] == "multiple":
                    choices = []
                    choices.append(decodeHTMLSymbols(
                        api_QA["results"][j]["correct_answer"]))
                    for ans in api_QA["results"][j]["incorrect_answers"]:
                        choices.append(decodeHTMLSymbols(ans))
                    question += "\nChoices:\n"
                    while len(choices) > 1:
                        i = random.randint(0, len(choices) - 1)
                        question += (choices[i] + "\n")
                        del choices[i]
                    question += choices[0]
                answer = decodeHTMLSymbols(
                    api_QA["results"][j]["correct_answer"])
                j += 1
            except KeyError as e:
                return await ctx.send("I have a bug in my API usage. Please open an issue with my creator and tell him\n", e)
            await ctx.send(str(player.member.name) + "\n" + question)
            try:
                msg = await client.wait_for('message', check=check(player.member), timeout=30)
            except asyncio.TimeoutError:
                msg = "No reply"
            if msg == "No reply":
                await ctx.send("The correct answer was " + answer)
            elif msg.content.lower() == answer.lower():
                await msg.add_reaction('✅')
                await ctx.send("correct!")
                player.score += 1
            elif msg.content.lower() == "i wish to quit":
                await ctx.send("Do you wish to quit " + (player.member.nick if player.member.nick != None else player.member.name) + "?")
                try:
                    msg = await client.wait_for('message', check=check(player.member), timeout=30)
                except asyncio.TimeoutError:
                    pass
                if msg.content.lower() == "yes":
                    player.quitting = True
                    await ctx.send("Alright quitter")
            else:
                await msg.add_reaction('❎')
                await ctx.send("Wrong. The correct answer was " + answer)
            if quitting:
                break
            await asyncio.sleep(2)
    await ctx.send("Thanks for playing here are the final results")
    final_results = ""
    for player in confirmed_players:
        if player.quitting:
            final_results += "~~" + \
                (player.member.nick if player.member.nick != None else player.member.name) + "'s~~ Quitter Score: " + \
                str(player.score) + "\n"
        else:
            final_results += (player.member.nick if player.member.nick != None else player.member.name) + \
                "'s Score: " + str(player.score) + "\n"
    await ctx.send(final_results)


async def bridge_of_death(ctx):
    colors = ["red", "green", "blue", "black", "white",
              "yellow", "orange", "brown", "pink", "purple", "gray", "grey"]
    await ctx.send("He who wishes to cross the bridge of Death, must answer me these questions three")
    await asyncio.sleep(2)
    await ctx.send('What is your name?')
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        return await failure(ctx)
    if not msg.content.lower() == ctx.author.name.lower() and not msg.content.lower() == ctx.author.nick.lower():
        return await failure(ctx)
    name = msg.content
    await ctx.send(name + '\nWhat is your favorite color?')
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        await failure(ctx)
        return
    if not msg.content.lower() in colors:
        await failure(ctx)
        return
    q3 = random.randint(1, 10)
    x = random.randint(1, 100)
    y = random.randint(1, 100)
    if q3 == 1:
        question = "What is " + str(x) + "+" + str(y) + "?"
        answer = str(x+y)
    elif q3 == 2:
        question = "What is " + str(x) + "-" + str(y) + "?"
        answer = str(x-y)
    elif q3 == 3:
        question = "What year is it?"
        answer = str(datetime.now().year)
    elif q3 == 4:
        question = "What is the airspeed velocity of an unladen swallow?"
        answer = "african or european?"
    elif q3 > 4:
        url = "https://opentdb.com/api.php?amount=1"
        try:
            api_QA = requests.get(url).json()
        except requests.exceptions.RequestException as e:
            return await ctx.send("I have a bug. Tell my creator\n" + e)
        question = ""
        try:
            if api_QA["results"][0]["type"] == "boolean":
                question += "True or False?\n"
            question += decodeHTMLSymbols(api_QA["results"][0]["question"])
            if api_QA["results"][0]["type"] == "multiple":
                choices = []
                choices.append(decodeHTMLSymbols(
                    api_QA["results"][0]["correct_answer"]))
                for ans in api_QA["results"][0]["incorrect_answers"]:
                    choices.append(decodeHTMLSymbols(ans))
                question += "\nChoices:\n"
                while len(choices) > 1:
                    i = random.randint(0, len(choices) - 1)
                    question += (choices[i] + "\n")
                    del choices[i]
                question += choices[0]
            answer = decodeHTMLSymbols(api_QA["results"][0]["correct_answer"])
        except KeyError as e:
            return await ctx.send("I have a bug in my API usage. Please open an issue with my creator and tell him\n" + e)
    else:
        return await ctx.send("You really should not be seeing this...")
    await ctx.send(name + "\n" + question)
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=15)
    except asyncio.TimeoutError:
        return await failure(ctx)
    print("The answer is :" + answer)
    if q3 == 4 and str(msg.content).lower() == answer.lower():
        await ctx.send("Huh? I… I don’t know that.")
        return await ctx.send("https://i.makeagif.com/media/8-06-2015/6tzcHH.gif")
    if not str(msg.content).lower() == answer.lower():
        return await failure(ctx)
    await ctx.send("Be on your way")
    return await ctx.send("https://tenor.com/view/monty-python-holy-grail-horse-gif-3448553")


# A math game that tormented me when I was younger because multiplication was hard
async def mad_minute(ctx):
    await ctx.send("You will have 1 minute to answer some multiplication problems. Good luck!")
    await asyncio.sleep(2)
    attempts = 0
    correct = 0
    await ctx.send("Go!")
    start = time.time()
    while time.time() - start <= 60:
        x = random.randint(0, 12)
        y = random.randint(0, 12)
        await ctx.send("What is " + str(x) + "x" + str(y) + "?")
        try:
            limit = 60 - (time.time() - start)
            msg = await client.wait_for('message', check=check(ctx.author), timeout=limit)
            if (msg.content == str(x*y)):
                correct += 1
            attempts += 1
        except asyncio.TimeoutError:
            pass
    if attempts != 0:
        await ctx.send("You made " + str(attempts) + " attempt(s) and got " + str(correct) + " correct")
    else:
        await ctx.send("You did nothing.")


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


async def failure(ctx):
    fails = ["https://tenor.com/view/monty-python-bridge-yellow-gif-9412030",
             "https://thumbs.gfycat.com/AlarmingBestBooby-mobile.mp4"]
    await ctx.send(fails[random.randint(0, len(fails) - 1)])


def decodeHTMLSymbols(str):
    str = str.replace("&Agrave;", "À").replace("&Aacute;", "Á").replace("&Acirc;", "Â").replace(
        "&Atilde;", "Ã").replace("&Auml;", "Ä").replace("&Aring;", "Å").replace("&agrave;", "à")
    str = str.replace("&aacute;", "á").replace("&acirc;", "â").replace("&atilde;", "ã").replace(
        "&auml;", "ä").replace("&aring;", "å").replace("&AElig;", "Æ").replace("&aelig;", "æ").replace("&szlig;", "ß")
    str = str.replace("&Ccedil;", "Ç").replace("&ccedil;", "ç").replace("&Egrave;", "È").replace(
        "&Eacute;", "É").replace("&Ecirc;", "Ê").replace("&Euml;", "Ë").replace("&egrave;", "è").replace("&eacute;", "é")
    str = str.replace("&ecirc;", "ê").replace("&euml;", "ë").replace("&#131;", "ƒ").replace("&Igrave;", "Ì").replace(
        "&Iacute;", "Í").replace("&Icirc;", "Î").replace("&Iuml;", "Ï").replace("&igrave;", "ì")
    str = str.replace("&iacute;", "í").replace("&icirc;", "î").replace("&iuml;", "ï").replace("&Ntilde;", "Ñ").replace(
        "&ntilde;", "ñ").replace("&Ograve;", "Ò").replace("&Oacute;", "Ó").replace("&Ocirc;", "Ô")
    str = str.replace("&Otilde;", "Õ").replace("&Ouml;", "Ö").replace("&ograve;", "ò").replace(
        "&oacute;", "ó").replace("&ocirc;", "ô").replace("&otilde;", "õ").replace("&ouml;", "ö").replace("&Oslash;", "Ø")
    str = str.replace("&oslash;", "ø").replace("&#140;", "Œ").replace("&#156;", "œ").replace("&#138;", "Š").replace(
        "&#154;", "š").replace("&Ugrave;", "Ù").replace("&Uacute;", "Ú").replace("&Ucirc;", "Û")
    str = str.replace("&Uuml;", "Ü").replace("&ugrave;", "ù").replace("&uacute;", "ú").replace(
        "&ucirc;", "û").replace("&uuml;", "ü").replace("&#181;", "µ").replace("&#215;", "×").replace("&Yacute;", "Ý")
    str = str.replace("&#159;", "Ÿ").replace("&yacute;", "ý").replace("&yuml;", "ÿ").replace(
        "&#176;", "°").replace("&#134;", "†").replace("&#135;", "‡").replace("&lt;", "<").replace("&gt;", ">")
    str = str.replace("&#177;", "±").replace("&#171;", "«").replace("&#187;", "»").replace(
        "&#191;", "¿").replace("&#161;", "¡").replace("&#183;", "·").replace("&#149;", "•").replace("&#153;", "™")
    str = str.replace("&copy;", "©").replace("&reg;", "®").replace('&quot;', '"').replace(
        "&#039;", "'").replace("&rsquo;", "’").replace("&lsquo;", "‘").replace("&shy;", "-").replace("&amp;", "&")
    str = str.replace("&micro;", "µ").replace("&pi;", "π").replace(
        "&ldquo;", '“').replace("&rdquo;", "”").replace("&deg;", "°")
    return str.strip()


def check(author):
    def inner_check(message):
        return message.author == author
    return inner_check


def KtoF(value):
    return ((value - 273.15)*1.8 + 32)


class SpeechQ:
    def __init__(self, textCh, speeches, connection, playing):
        self.textCh = textCh
        self.connection = connection
        self.playing = playing
        self.speeches = speeches


class GameShow:
    def __init__(self, member, score=0, quitting=False):
        self.member = member
        self.score = score
        self.quitting = quitting


async def TTStime(ctx, speak, lang, say=None, rate=None, name=""):
    if not say:
        temp = ctx.message.content.lower().split(speak)
        temp = await shift(temp)
        speech = await join(temp, speak)
    else:
        speech = say
    v_channel = ctx.message.author.voice
    if v_channel:
        if ctx.message.author.voice.self_deaf or ctx.message.author.voice.deaf:
            return await ctx.message.channel.send("you aren't going to listen to me anyways")
        serverQueue = queue.get(ctx.message.guild.id)
        millis = int(round(time.time() * 1000))
        # no name conflicts should be possible
        file = "voice" + str(millis) + \
            str(ctx.message.author.id) + name + ".mp3"
        if not rate:
            rate = 175
        if serverQueue != None:
            return serverQueue.speeches.append((speech, file, rate, lang))
        try:
            voice_client = discord.utils.get(
                client.voice_clients, guild=ctx.message.guild)
            if voice_client and voice_client.is_connected():
                serverQueue = SpeechQ(ctx.message.channel, [
                                      (speech, file, rate, lang)], voice_client, 1)
                queue.update({ctx.message.guild.id: serverQueue})
            else:
                connection = await v_channel.channel.connect(timeout=20, reconnect=True)
                serverQueue = SpeechQ(ctx.message.channel, [
                                      (speech, file, rate, lang)], connection, 1)
                queue.update({ctx.message.guild.id: serverQueue})
            play_next(ctx.message.guild)
        except discord.errors.ClientException:
            return
        except Exception as e:
            print(e)
            print("Exception?")
            await connection.disconnect(force=True)
    else:
        await ctx.message.channel.send("you are not in a voice channel")


def play_next(guild):
    serverQueue = queue.get(guild.id)
    if not serverQueue:
        return

    if len(serverQueue.speeches) == 0:
        queue.pop(guild.id)
        future = asyncio.run_coroutine_threadsafe(
            serverQueue.connection.disconnect(), client.loop)
        try:
            future.result(timeout=60)
        except asyncio.TimeoutError:
            print('The coroutine took too long, cancelling the task...')
            return future.cancel()
    else:
        tupleQ = serverQueue.speeches.pop(0)
        create_voice(tupleQ)
        # the mp3 file is not ready right away
        time.sleep(len(tupleQ[0]) * .005)
        serverQueue.connection.play(discord.FFmpegPCMAudio(
            tupleQ[1]), after=lambda x: clean_up(guild, tupleQ[1]))
    return


def clean_up(guild, file):
    if file:
        os.remove(file)
    play_next(guild)


def create_voice(tupleQ):
    engine = pyttsx3.init()
    engine.setProperty('rate', tupleQ[2])
    voices = engine.getProperty('voices')
    voice = voices[tupleQ[3]]
    engine.setProperty('voice', voice.id)
    engine.save_to_file(tupleQ[0], tupleQ[1])
    engine.runAndWait()
    engine.stop()


async def join(list, word):
    limit = len(list)
    if (limit == 1):
        return list[0]
    str = ""
    i = 0
    for item in list:
        str += item
        i += 1
        if (i != limit):
            str += word
    return str


async def shift(list):
    temp = []
    i = 1
    while i < len(list):
        temp.append(list[i])
        i += 1
    return temp

client.run(config['bot-token']['token'])
