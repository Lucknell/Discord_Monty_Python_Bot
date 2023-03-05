from cogs.lucknell.lyrics import lyric_finder, SongNotFoundError
from discord.ext import commands
import discord


class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "lyrics", with_app_command = True, description ="Search for lyrics")
    async def lyrics(self, ctx, song):
        if not song:
            return await ctx.send("I need something to look up lyrics for.")
        msg = await ctx.send("Searching for {}".format(song))
        try:
            lyric = lyric_finder(song, "genius")
        except SongNotFoundError:
            return await ctx.send("Song `{}` not found".format(song))
        embed = discord.Embed()
        embed.add_field(name=lyric.title + " by " + lyric.author, value="‎‎")
        if len(lyric.lyrics) < 1024:
            embed.add_field(name="‎‎", value=lyric.lyrics)
        else:
            lyrics = lyric.lyrics.split("\n\n")
            chars = len(lyric.title) + len("‎‎")
            for line in lyrics:
                temp = ""
                if len(line) == 0:
                    continue
                if len(line) > 1024:
                    for word in line.split("\n"):
                        if chars + len(temp) + len(word) >= 4500:
                            await ctx.send(embed=embed)
                            embed = discord.Embed()
                            chars = 0
                        if len(temp) + len(word) + 1 < 1024:
                            temp += word + "\n"
                        else:
                            embed.add_field(name="‎‎", value=temp, inline=True)
                            chars += len(temp) + 2
                            temp = word + "\n"
                    embed.add_field(name="‎‎", value=temp, inline=True)
                    continue
                if chars + len(line) + len(temp) >= 4500:
                    await ctx.send(embed=embed)
                    embed = discord.Embed()
                    chars = 0
                chars += len(line) + 2 
                embed.add_field(name="‎‎", value=line, inline=True)
        embed.add_field(
            name="Link", value="[Click here]({})".format(lyric.URL))
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
        return await msg.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Lyrics(bot))
