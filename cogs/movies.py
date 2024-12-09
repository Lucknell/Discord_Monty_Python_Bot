from discord.ext import commands
import discord
from cogs.lucknell.movies import Movie_Finder, MovieNotFoundError

class Movies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "movies", with_app_command = True, description ="Get Movies info")
    async def Movies(self, ctx: commands.Context):
        await ctx.defer()
        try:
            Movies = Movie_Finder()
        except MovieNotFoundError:
            return await ctx.send("No results found")
        embed = discord.Embed()
        #embed.set_author(name=Movies.heading)
        #embed.add_field(name="Type", value=Movies.type)
        #self, title, release_date, poster, trailer, rating, runtime
        for title, params in Movies.movies.items():
            value = f"Release Date: {params.release_date}\nTrailer: {params.trailer}\nRating:{params.rating}\nRuntime:{params.runtime}"
            embed.add_field(name=title, value=value)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Movies(bot))