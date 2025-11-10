import discord
from discord.ext import commands
from cogs.lucknell.yugi import yugioh_finder, ShadowRealmError


class Yugioh(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "yugi", with_app_command = True, description ="It's time to duel")
    async def yugioh(self, ctx: commands.Context, search: str):
        if not search:
            return await ctx.send("Please give a string to search with")
        try:
            yugioh = yugioh_finder(search)
        except ShadowRealmError:
            return await ctx.send("No results found")
        embed = discord.Embed()
        if yugioh.picture:
            embed.set_image(url=yugioh.picture)
        embed.set_author(name=yugioh.heading)
        #embed.add_field(name="Type", value=yugioh.type)
        embed.add_field(name="Description", value=yugioh.description)
        if yugioh.isACard and yugioh.card_type == "Monster":
            embed.add_field(name="Type", value=yugioh.type)
            embed.add_field(name="Level", value=yugioh.level)
            embed.add_field(name="ATK/DEF", value=yugioh.stats)    
        embed.add_field(name="URL", value=yugioh.URL)
        try:
            await ctx.send(embed=embed)
        except discord.errors.HTTPException:
            await ctx.send("Your search results were sent to the Shadow Realm")

async def setup(bot):
    await bot.add_cog(Yugioh(bot))