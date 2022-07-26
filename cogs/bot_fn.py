import utils
from discord.ext import commands
import discord
import sys
import asyncio
import random
import requests
import os
import pytesseract
import numpy as np
from datetime import datetime
from PIL import Image
import shutil
sys.path.append("/src/bot/cogs/lucknell/")


class Monty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        statuses = ["Jokes on you we still alive", "I'm fine, get X go", "Systems online awaiting next task",
                    "Damage report returned. No damage found", "You scared ain't ya?"]
        # randInt is inclusive of the upper bound
        return await ctx.send(statuses[random.randint(0, len(statuses) - 1)])

    @commands.command()
    async def totext(self, ctx, arg=None):
        if not arg:
            return await ctx.send("Try that again but give me a URL to an image next time")
        url = utils.valid_URL(arg)
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

    @commands.command()
    async def good(self, ctx, arg):
        if arg.lower() == "bot":
            await ctx.message.add_reaction("😄")

    @commands.command()
    async def bad(self, ctx, arg):
        if arg.lower() == "bot":
            await ctx.send("alright then.")

    @commands.command()
    async def about(self, ctx):
        return await ctx.send("You can learn more about me here\nhttps://github.com/Lucknell/Discord_Monty_Python_Bot")

    @commands.command(aliases=['poll'])
    async def vote(self, ctx):
        current = ['0️⃣', '1️⃣', '2️⃣', '3️⃣',
                   '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        await ctx.send("What do you want to put to a vote " + ctx.author.mention + "?\nComma separate the items (max 10)")
        try:
            msg = await self.bot.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("On this day the vote was canceled before starting.")
        choices = msg.content.split(",")
        if len(choices) < 2:
            return await ctx.send("Not enough choices to make the poll")
        if len(choices) > 10:
            return await ctx.send("Too many choices")
        i = -1
        s = "Here are the choices react below"
        vote = await ctx.send("loading...")
        for choice in choices:
            i += 1
            s += "\n" + current[i] + ": " + choice
        s += "\npoll id is: {}".format(vote.id)
        for emoji in current[:len(choices)]:
            await vote.add_reaction(emoji)
        await vote.edit(content=s)

    @commands.command()
    async def count(self, ctx, id=None):
        if not id:
            return
        poll = await ctx.channel.fetch_message(id)
        if not poll.content.endswith("poll id is: {}".format(id)):
            return await ctx.send("invalid poll")
        current = ['0️⃣', '1️⃣', '2️⃣', '3️⃣',
                   '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        valid_voters = [self.bot.user.id]

        count = len(poll.content.split("\n")) - 2
        options = {x[:3]: x[4:] for x in poll.content.split("\n")[1:count+1]}
        tally = {x: 0 for x in current[:count]}
        for reaction in poll.reactions:
            if reaction.emoji in current[:count]:
                voters = await reaction.users().flatten()
                for voter in voters:
                    if voter.id not in valid_voters:
                        tally[reaction.emoji] += 1
                        valid_voters.append(voter.id)
        results = "Final results\n"
        results += "\n".join(['{}: {}'.format(options[key], tally[key])
                              for key in tally.keys()])
        await ctx.send(results)
        await poll.delete()

    @commands.command()
    async def reaction(self, ctx, id=None, *, phrases=None):
        if not id or not phrases:
            return await ctx.send("I need a message id like {} and a phrase like **uncopyrightable**".format(ctx.message.id))
        try:
            msg = await ctx.channel.fetch_message(id)
        except discord.errors.NotFound:
            return await ctx.send("invalid id")
        except discord.errors.HTTPException:
            return await ctx.send("invalid id")
        letters = []
        emojis = {"a": "🇦",
                  "b": "🇧",
                  "c": "🇨",
                  "d": "🇩",
                  "e": "🇪",
                  "f": "🇫",
                  "g": "🇬",
                  "h": "🇭",
                  "i": "🇮",
                  "j": "🇯",
                  "k": "🇰",
                  "l": "🇱",
                  "m": "🇲",
                  "n": "🇳",
                  "o": "🅾️",
                  "p": "🅿️",
                  "q": "🇶",
                  "r": "🇷",
                  "s": "🇸",
                  "t": "🇹",
                  "u": "🇺",
                  "v": "🇻",
                  "w": "🇼",
                  "x": "🇽",
                  "y": "🇾",
                  "z": "🇿",
                  "#": "#️⃣",
                  "0": "0️⃣",
                  "1": "1️⃣",
                  "2": "2️⃣",
                  "3": "3️⃣",
                  "4": "4️⃣",
                  "5": "5️⃣",
                  "6": "6️⃣",
                  "7": "7️⃣",
                  "8": "8️⃣",
                  "9": "9️⃣"}
        phrase = phrases.lower().split(" ")
        phrases = await utils.join(phrase, "")
        for letter in str(phrases):
            if not letter in letters:
                letters.append(letter)
            else:
                return await ctx.send("https://tenor.com/view/invader-zim-movie-enter-the-gif-14899370")
        for letter in letters:
            try:
                await msg.add_reaction(emojis[letter])
            except KeyError:
                pass

    @commands.command()
    async def flip(self, ctx):
        coin = random.randint(0, 1)
        if coin == 1:
            return await ctx.send("Heads")
        else:
            return await ctx.send("Tails")

    @commands.command()
    async def report(self, ctx, word="", user=None):
        client = self.bot
        if word.lower() != "card":
            return
        if user == None:
            await ctx.send("For who?")
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                msg = None
            if msg:
                member = msg.content.split(" ")[0]
                try:
                    player = await msg.guild.fetch_member(int(member.replace("<", "").replace(">", "").replace("@", "").replace("!", "")))
                except discord.errors.NotFound:
                    player = client.user
                except discord.errors.HTTPException:
                    player = client.user
                except ValueError:
                    player = client.user
        else:
            try:
                player = await ctx.message.guild.fetch_member(int(user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")))
            except discord.errors.NotFound:
                player = client.user
            except discord.errors.HTTPException:
                player = client.user
            except ValueError:
                player = client.user
        card = discord.Embed(
        title="Report card for {} in {}".format(player.display_name, ctx.message.guild.name))
        card.add_field(name="Math", value="F")
        card.add_field(name="Reading", value="F")
        card.add_field(name="English", value="F")
        card.add_field(name="History", value="F")
        card.add_field(name="Science", value="F")
        card.add_field(name="Music", value="F")
        await ctx.send(embed=card)
        

def setup(bot):
    bot.add_cog(Monty(bot))
