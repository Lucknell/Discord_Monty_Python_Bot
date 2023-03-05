import os
import discord
import rlvoice
import time
import asyncio
import random
import re

queue = {}
connected = {}


class SpeechQ:
    def __init__(self, textCh, speeches, connection, playing):
        self.textCh = textCh
        self.connection = connection
        self.playing = playing
        self.speeches = speeches


async def TTStime(ctx, speak, lang, client, say=None, rate=None, name=""):
    await ctx.send("Attempting...", ephemeral = True)
    if not say:
        temp = ctx.message.content.lower().split(speak)
        temp = await shift(temp)
        speech = await join(temp, speak)
    else:
        speech = say
    connection = None
    v_channel = ctx.message.author.voice
    if len(speech) < 6:
        return await ctx.send("too little to speak make your phrase longer")
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
                connected.update({ctx.message.guild.id: connection})
            play_next(ctx.message.guild, client)
        except discord.errors.ClientException:
            return await connection.disconnect(force=True)
        except Exception as e:
            print(e)
            print("Exception?")
            if connection:
                await connection.disconnect(force=True)
    else:
        await ctx.message.channel.send("you are not in a voice channel")


def play_next(guild, client):
    serverQueue = queue.get(guild.id)
    if not serverQueue:
        return

    if len(serverQueue.speeches) == 0:
        queue.pop(guild.id)
        future = asyncio.run_coroutine_threadsafe(
            asyncio.sleep(120), client.loop)
        try:
            future.result(timeout=121)
        except asyncio.TimeoutError:
            print('The coroutine took too long, cancelling the task...')
        q = queue.get(guild.id)
        if q:
            return
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
        time.sleep(len(tupleQ[0]) * .007)
        if not os.path.isfile(tupleQ[1]):
            future = asyncio.run_coroutine_threadsafe(
                serverQueue.textCh.send("An error occurred. Sorry about that"))
            try:
                future.result(timeout=30)
            except asyncio.TimeoutError:
                print('The coroutine took too long, cancelling the task...')
        serverQueue.connection.play(discord.FFmpegPCMAudio(
            tupleQ[1]), after=lambda x: clean_up(guild, tupleQ[1], client))
    return


def clean_up(guild, file, client):
    if file:
        try:
            os.remove(file)
        except FileNotFoundError as e:
            print(e)
    play_next(guild, client)


def create_voice(tupleQ):
    engine = rlvoice.init()
    engine.setProperty('rate', tupleQ[2])
    voices = engine.getProperty('voices')
    voice = voices[tupleQ[3]]
    engine.setProperty('voice', voice.id)
    engine.save_to_file(tupleQ[0], tupleQ[1])
    engine.runAndWait()
    engine.stop()


async def dc(ctx):
    if ctx.message.author.voice and ctx.message.author.voice.channel:
        connection = connected.get(ctx.message.guild.id)
        if connection == None:
            return await ctx.send("Not connected")
        await connection.disconnect()
        await ctx.send("That's all folks!")
        queue.pop(ctx.message.guild.id)
        connected.pop(ctx.message.guild.id)
    else:
        await ctx.send("You are not in a voice channel")


async def skip(ctx):
    if not ctx.message.author.voice.channel:
        return
    serverQueue = queue.get(ctx.message.guild.id)
    if serverQueue == None:
        return
    serverQueue.connection.stop()


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


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


def valid_URL(str):
    return re.search(r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$", str)


def check(author):
    def inner_check(message):
        return message.author == author
    return inner_check


def KtoF(value):
    return ((value - 273.15)*1.8 + 32)


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
