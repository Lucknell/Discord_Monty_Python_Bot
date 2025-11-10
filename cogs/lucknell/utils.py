import os
import re
import time
import wave
import random
import discord
import rlvoice
import asyncio
import traceback
from piper.voice import PiperVoice

queue = {}
connected = {}


class SpeechQ:
    def __init__(self, textCh, speeches, connection, playing):
        self.textCh = textCh
        self.connection = connection
        self.playing = playing
        self.speeches = speeches

async def create_voice_and_play(ctx, speech, client):
    await ctx.send(f"Attempting to say:{speech}")
    connection = None
    v_channel = ctx.message.author.voice
    if not v_channel:
        return await ctx.message.channel.send("you are not in a voice channel")
    if ctx.message.author.voice.self_deaf or ctx.message.author.voice.deaf:
        return await ctx.message.channel.send("you aren't going to listen to me anyways")
    voice_queue = queue.get(ctx.message.guild.id)
    millis = int(round(time.time() * 1000))
    # no name conflicts should be possible
    file = f"voice{millis}{ctx.message.author.id}.wav"
    if voice_queue != None:
        return voice_queue.speeches.append((speech, file))
    try:
        voice_client = discord.utils.get(
            client.voice_clients, guild=ctx.message.guild)
        if voice_client and voice_client.is_connected():
            voice_queue = SpeechQ(ctx.message.channel, [
                                  (speech, file)], voice_client, 1)
            queue.update({ctx.message.guild.id: voice_queue})
        else:
            connection = await v_channel.channel.connect(timeout=20, reconnect=True)
            voice_queue = SpeechQ(ctx.message.channel, [
                                  (speech, file)], connection, 1)
            queue.update({ctx.message.guild.id: voice_queue})
            connected.update({ctx.message.guild.id: connection})
        await play_next(ctx.message.guild, client)
    except discord.errors.ClientException:
        return await connection.disconnect(force=True)
    except Exception as e:
        client.logger.error(e)
        traceback.print_exc()
        client.logger.error("Exception?")
        if connection:
            await connection.disconnect(force=True)


async def play_next(guild, client):
    voice_queue = queue.get(guild.id)
    if not voice_queue:
        return

    if len(voice_queue.speeches) == 0:
        queue.pop(guild.id)
        q = queue.get(guild.id)
        if q:
            return
    curr_voice = voice_queue.speeches.pop(0)
    create_voice(curr_voice)
    voice_queue.connection.play(discord.FFmpegPCMAudio(
        curr_voice[1]), after=lambda x: asyncio.run_coroutine_threadsafe(clean_up(guild, curr_voice[1], client), client.loop))
    return


async def clean_up(guild, file, client):
    if file:
        try:
            os.remove(file)
        except FileNotFoundError as e:
            client.logger.error(e)
    await play_next(guild, client)


def create_voice(curr_voice):
    model = "/src/bot/models/en_US-amy-medium.onnx"
    voice = PiperVoice.load(model)
    wav_file = wave.open(curr_voice[1], "w")
    audio = voice.synthesize(curr_voice[0], wav_file)
    
    

async def dc(ctx):
    if ctx.message.author.voice and ctx.message.author.voice.channel:
        connection = connected.get(ctx.message.guild.id)
        if connection == None:
            return await ctx.send("Not connected")
        await connection.disconnect()
        await ctx.send("That's all folks!")
        try:
            queue.pop(ctx.message.guild.id)
        except KeyError as e:
            pass
        connected.pop(ctx.message.guild.id)
        
    else:
        await ctx.send("You are not in a voice channel")


async def skip(ctx):
    if not ctx.message.author.voice.channel:
        return
    voice_queue = queue.get(ctx.message.guild.id)
    if voice_queue == None:
        return
    voice_queue.connection.stop()


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

def check_interaction_from_user(author):
    def inner_check(interaction):
        return interaction.user == author
    return inner_check

def check_interaction(author):
    def inner_check(interaction):
        return interaction.data["component_type"] == 2 and "custom_id" in interaction.data.keys() and interaction.user == author
    return inner_check

def check_select_interaction(author):
    def inner_check(interaction):
        return interaction.data["component_type"] == 3 and "custom_id" in interaction.data.keys() and interaction.user == author
    return inner_check

def check_userselect_interaction(author):
    def inner_check(interaction):
        return interaction.data["component_type"] == 5 and "custom_id" in interaction.data.keys() and interaction.user == author
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
