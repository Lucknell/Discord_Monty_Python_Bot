from discord.ext import commands
import discord
import requests
import sys
sys.path.append("/src/bot/cogs/lucknell/")
import utils

class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joke(self, ctx):
        headers = {"Accept": "application/json"}
        url = "https://icanhazdadjoke.com/"
        joke_data = requests.get(url, headers=headers).json()
        await ctx.send(joke_data["joke"])
        if ctx.message.author.voice:
            await utils.TTStime(ctx, "", 17, self.bot, joke_data["joke"])


    @commands.command()
    async def fact(self, ctx):
        headers = {"Accept": "application/json"}
        url = "https://useless-facts.sameerkumar.website/api"
        fact_data = requests.get(url, headers=headers).json()
        await ctx.send(fact_data["data"])

def setup(bot):
    bot.add_cog(Joke(bot))