from lyrics import lyric_finder, SongNotFoundError
from discord.ext import commands
import discord
import sys
sys.path.append("/src/bot/cogs/lucknell/")


class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['lyric'])
    async def lyrics(self, ctx, *, song):
        await ctx.send("Searching for {}".format(song))
        try:
            lyric = lyric_finder(song, "genius")
        except SongNotFoundError:
            return await ctx.send("Song `{}` not found".format(song))
        embed = discord.Embed()
        embed.add_field(name=lyric.title, value="‎‎")
        if len(lyric.lyrics) < 1024:
            embed.add_field(name="‎‎", value=lyric.lyrics)
        else:
            lyrics = lyric.lyrics.split("\n\n")
            for line in lyrics:
                if len(line) < 1:
                    continue
                if len(line) > 1024:
                    temp = ""
                    for bar in line.split("\n"):
                        if len(temp) + len(bar) + 1 < 1024:
                            temp += bar + "\n"
                        else:
                            embed.add_field(name="‎‎", value=temp, inline=True)
                            temp = bar
                    embed.add_field(name="‎‎", value=temp, inline=True)
                    continue
                embed.add_field(name="‎‎", value=line, inline=True)
        embed.add_field(
            name="Link", value="[Click here]({})".format(lyric.URL))
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Lyrics(bot))
