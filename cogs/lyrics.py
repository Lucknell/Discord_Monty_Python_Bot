from cogs.lucknell.lyrics import lyric_finder, SongNotFoundError
from discord.ext import commands
import discord
import math


class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "lyrics", with_app_command = True, description ="Search for lyrics")
    async def lyrics(self, ctx, song):
        if not song:
            return await ctx.send("I need something to look up lyrics for.")
        await ctx.defer()
        try:
            lyric = lyric_finder(song, "genius")
        except SongNotFoundError:
            return await ctx.send("Song `{song}` not found")
        embed = discord.Embed()
        embed.add_field(name=f"{lyric.title} by {lyric.author}", value="‎‎")
        if len(lyric.lyrics) < 1024:
            embed.add_field(name="‎‎", value=lyric.lyrics)
        else:
            interactions = math.ceil(len(lyric.lyrics) / 1024)#name this parts 
            for x in range(interactions):
                embed.add_field(name="‎‎", value=lyric.lyrics[x*1024:(x+1)*1024])
        embed.add_field(
            name="Link", value=f"[Click here]({lyric.URL})")
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
        logger.info(lyric.lyrics)
        return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Lyrics(bot))
