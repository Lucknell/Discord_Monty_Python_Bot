from discord.ext import commands
import discord
import requests
import sys
sys.path.append("/src/bot/cogs/lucknell/")
import utils

class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "joke", with_app_command = True, description ="try it out and see")
    async def joke(self, ctx: commands.Context):
        headers = {"Accept": "application/json"}
        url = "https://icanhazdadjoke.com/"
        joke_data = requests.get(url, headers=headers).json()
        await ctx.send(joke_data["joke"])

    @commands.hybrid_command(name = "fact", with_app_command = True, description ="These may be true")
    async def fact(self, ctx: commands.Context):
        headers = {"Accept": "application/json"}
        url = "https://useless-facts.sameerkumar.website/api"
        fact_data = requests.get(url, headers=headers).json()
        await ctx.send(fact_data["data"])

async def setup(bot):
    await bot.add_cog(Joke(bot))
