from urban_dict import urban_finder, SongNotFoundError
from discord.ext import commands
import discord
import sys
sys.path.append("/src/bot/cogs/lucknell/")


class Urban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "urban_dict", with_app_command = True, description ="Search the true dictionary")
    async def urban(self, ctx: commands.Context, phrase: str):
        if not phrase:
            return await ctx.send("I need something to look up on urban dictionary.")
        await ctx.send("Searching for {}".format(phrase))
        try:
            definition = urban_finder(phrase)
        except SongNotFoundError:
            return await ctx.send("phrase `{}` not found".format(phrase))
        embed = discord.Embed()
        embed.add_field(name=definition.title[0:256], value="‎‎")
        embed.add_field(name="Definition", value=definition.definition)
        embed.add_field(name="Example", value=definition.example)
        embed.set_footer(text="Found for " + ctx.author.name, icon_url=ctx.author.avatar_url)

        return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Urban(bot))
