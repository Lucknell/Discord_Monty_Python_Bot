from discord.ext import commands
import discord
import requests
import sys
sys.path.append("/src/bot/cogs/lucknell/")
from dictt import word_search, WordNotFoundError
 
class Words(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "define", with_app_command = True, description ="Search for a definition")
    async def define(self, ctx: commands.Context, search: str):
        if not search:
            return await ctx.send("Please give a word to define")
        
        embed = discord.Embed()
        try:
            dictionary = word_search(search)
        except WordNotFoundError:
            await ctx.send("Either that was not a word or my library is broken")
        embed.add_field(name=dictionary.title, value="‎‎")
        embed.add_field(name="Type", value=dictionary.type)
        embed.add_field(name="Definition", value=dictionary.definition[0:1024])
        embed.add_field(name="URL", value=dictionary.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Words(bot))
