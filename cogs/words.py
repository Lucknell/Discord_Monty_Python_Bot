from discord.ext import commands
import discord
import requests

class Words(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def define(self, ctx, search=None):
        if not search:
            return await ctx.send("Please give a word to define")
        URL = "https://api.dictionaryapi.dev/api/v2/entries/en_US/{}".format(search)
        dictionary = requests.get(URL).json()
        word = dictionary[0]["word"]
        embed = discord.Embed()
        embed.add_field(name=word, value="‎‎")
        count = 1
        for definition in dictionary[0]["meanings"]:
           embed.add_field(name="definition {}".format(count), value=definition["definitions"][0]["definition"]) 
           count += 1
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Words(bot))