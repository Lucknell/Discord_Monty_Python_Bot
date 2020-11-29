import os
import discord
import pyttsx3
import time
import asyncio
import requests
import random
import configparser

from datetime import datetime
from discord.ext import commands

client = commands.Bot(command_prefix=commands.when_mentioned_or('$'))
client.remove_command('help')  # remove the default help message

config = configparser.ConfigParser()
config.read('config.ini')

avatar_path = "/src/bot/avatar.png"
fp = open(avatar_path, 'rb')
avatar = fp.read()

helpMessage = discord.Embed(
    title="Help message and the quest for the holy grail",
    color=discord.Color(0xff94aa),
    timestamp=datetime.now()
)
helpMessage.set_footer(text="plz send help I have been on since")
helpMessage.add_field(name="commands", value="$dc\n$status\n$game\n")
helpMessage.add_field(name="voice chat commands",
                      value="$say something\n$parler omelette au fromage\n$hablar tengo un gato en mis pantalones\n$skazat медведь на одноколесном велосипеде\n$zip 33016\n$dire something italian")
helpMessage.add_field(
    name="Games", value="I wish to cross the bridge of death\nMad Minute")
queue = {}


@client.event
async def on_ready():
    print('And the holy grail')
    await client.user.edit(avatar=avatar)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Holy Grail"))


@client.command()
async def help(ctx):
    await ctx.send(embed=helpMessage)


@client.command()
async def say(ctx):
    await TTStime(ctx.message, "say", 17)


@client.command()
async def skazat(ctx):
    await TTStime(ctx.message, "skazat", 54)


@client.command()
async def hablar(ctx):
    await TTStime(ctx.message, "hablar", 18)


@client.command()
async def parler(ctx):
    await TTStime(ctx.message, "parler", 24)


@client.command()
async def dire(ctx):
    await TTStime(ctx.message, "dire", 34)


@client.command()
async def hanasu(ctx):
    await TTStime(ctx.message, "hanasu", 39)


@client.command()
async def game(ctx):
    await ctx.send("What do you want to do " + str(ctx.author.name) + "?")
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        return await ctx.send("https://tenor.com/view/game-over-insert-coins-gif-12235828")
    if msg.content.lower() == "i wish to cross the bridge of death":
        await ctx.send("He who wishes to cross the bridge of Death, must answer me these questions three")
        await asyncio.sleep(2)
        await bridge_of_death(ctx)
    elif msg.content.lower() == "mad minute":
        await ctx.send("You will have 1 minute to answer some multiplication problems. Good luck!")
        await asyncio.sleep(2)
        await mad_minute(ctx)
    else:
        return await ctx.send("You what?")


@client.command()
async def dc(ctx):
    x = ctx.message.author.voice.channel
    if x:
        serverQueue = queue.get(ctx.message.guild.id)
        if(serverQueue == None):
            return
        await serverQueue.connection.disconnect()
        for f in serverQueue.speeches:
            os.remove(f)
        queue.pop(ctx.message.guild.id)


@client.command()
async def status(ctx):
    return await ctx.send('Jokes on you we still alive')


@client.command()
async def zip(ctx):
    API_key = config['openweathermap']['api_key']
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    zip_code = ctx.message.content.lower().split("zip ")
    if len(zip_code) != 2:
        return await ctx.send("That is a format error. Please get some $help")
    Final_url = base_url + "appid=" + API_key + "&zip=" + zip_code[1].strip()
    weather_data = requests.get(Final_url).json()
    print(weather_data)
    if weather_data["cod"] == "404":
        return await ctx.send("invalid zipcode")
    temp = weather_data["main"]["temp"]
    temp = str(round(KtoF(temp), 1))
    weather_talk = "Currently the weather for " + \
        weather_data["name"] + " is, " + weather_data["weather"][0]["main"] + \
        " with " + weather_data["weather"][0]["description"]
    weather_talk += ", the temperature is " + \
        temp.replace(".", " point ", 1) + \
        " degrees Fahrenheit. the rest is coming soon because I don't fully work yet. Have a good day "
    weather_talk += ctx.message.author.name
    print(weather_talk)
    await TTStime(ctx.message, "", 14, say=weather_talk, rate=125)


async def bridge_of_death(ctx):
    colors = ["red", "green", "blue", "black", "white",
              "yellow", "orange", "brown", "pink", "purple", "gray"]
    await ctx.send('What is your name?')
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        await failure(ctx)
        return
    if not msg.content.lower() == str(ctx.author.name).lower():
        await failure(ctx)
        return
    await ctx.send('What is your favorite color?')
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=60)
    except asyncio.TimeoutError:
        await failure(ctx)
        return
    if not msg.content.lower() in colors:
        await failure(ctx)
        return
    q3 = random.randint(1, 6)
    x = random.randint(1, 100)
    y = random.randint(1, 100)
    if q3 == 1:
        question = "What is " + str(x) + "+" + str(y) + "?"
        answer = str(x+y)
    elif q3 == 2:
        question = "What is " + str(x) + "-" + str(y) + "?"
        answer = str(x-y)
    elif q3 == 3:
        question = "What is " + str(x) + "x" + str(y) + "?"
        answer = str(x*y)
    elif q3 == 4:
        question = "What is " + str(x) + "/" + str(y) + "?"
        answer = str(x/y)
    elif q3 == 5:
        question = "What year is it?"
        answer = str(datetime.now().year)
    elif q3 == 6:
        question = "What is the airspeed velocity of an unladen swallow?"
        answer = "african or european?"
    else:
        return await ctx.send("You really should not be seeing this...")
    await ctx.send(question)
    try:
        msg = await client.wait_for('message', check=check(ctx.author), timeout=15)
    except asyncio.TimeoutError:
        return await failure(ctx)
    print(answer)
    if not str(msg.content) == answer:
        return await failure(ctx)
    await ctx.send("Be on your way")
    return await ctx.send("https://tenor.com/view/monty-python-holy-grail-horse-gif-3448553")


# A math game that tormented me when I was younger because multiplication was hard


async def mad_minute(ctx):
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


async def failure(ctx):
    await ctx.send("https://thumbs.gfycat.com/AlarmingBestBooby-mobile.mp4")


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


async def TTStime(message, speak, lang, say=None, rate=None):
    if not say:
        temp = message.content.lower().split(speak)
        temp = await shift(temp)
        speech = await join(temp, speak)
    else:
        speech = say
    v_channel = message.author.voice.channel
    if v_channel:
        if message.author.voice.self_deaf or message.author.voice.deaf:
            return await message.channel.send("you aren't going to listen to me anyways")
        serverQueue = queue.get(message.guild.id)
        millis = int(round(time.time() * 1000))
        # no name conflicts should be possible
        file = "voice" + str(millis) + str(message.author.id) + ".mp3"
        engine = pyttsx3.init()
        if not rate:
            engine.setProperty('rate', 175)
        else:
            engine.setProperty('rate', rate)
        voices = engine.getProperty('voices')
        voice = voices[lang]
        engine.setProperty('voice', voice.id)
        engine.save_to_file(speech, file)
        engine.runAndWait()
        if serverQueue != None:
            serverQueue.speeches.append(file)
            return
        try:
            voice_client = discord.utils.get(
                client.voice_clients, guild=message.guild)
            if voice_client and voice_client.is_connected():
                serverQueue = SpeechQ(message.channel, [file], voice_client, 1)
                queue.update({message.guild.id: serverQueue})
            else:
                connection = await v_channel.connect(timeout=20, reconnect=True)
                serverQueue = SpeechQ(message.channel, [file], connection, 1)
                queue.update({message.guild.id: serverQueue})
            play(message.guild, file)
        except Exception as e:
            print(e)
            print("Exception?")
            await connection.disconnect(force=True)
    else:
        message.channel.send("you are not in a voice channel")


def play(guild, filename):
    serverQueue = queue.get(guild.id)
    if(filename == None):
        queue.pop(guild.id)
    serverQueue.connection.play(discord.FFmpegPCMAudio(
        filename), after=lambda x: play_next(guild))


def play_next(guild):
    serverQueue = queue.get(guild.id)
    # in the event that the bot has dc called this catches the empty queue and ignores it.
    try:
        os.remove(serverQueue.speeches[0])
        serverQueue.speeches.pop(0)
    except Exception:
        pass

    if len(serverQueue.speeches) == 0:
        queue.pop(guild.id)
        future = asyncio.run_coroutine_threadsafe(
            serverQueue.connection.disconnect(), client.loop)
        try:
            future.result(timeout=1)
        except asyncio.TimeoutError:
            print('The coroutine took too long, cancelling the task...')
            future.cancel()
    else:
        serverQueue.connection.play(discord.FFmpegPCMAudio(
            serverQueue.speeches[0]), after=lambda x: play_next(guild))
    return


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
