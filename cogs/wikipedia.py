from discord.ext import commands
import discord
import sys
sys.path.append("/src/bot/cogs/lucknell/")
from wikipedia import wikipedia

class Wiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "wiki", with_app_command = True, description ="Search wikipedia for information")
    async def wiki(self, ctx: commands.Context, search: str):
        wiki = wikipedia(search)
        try:
            return await ctx.send("{} \nRead more here: {}".format(wiki.summary, wiki.url))
        except AttributeError:
            return await ctx.send("No articles found")
        except discord.errors.HTTPException:
            await ctx.send(wiki.summary[0:2000])
            return await ctx.send("Read more here: {}".format(wiki.url))


    @commands.hybrid_command(name = "wiki_table", with_app_command = True, description ="Search wikipedia for information")
    async def wiki_info(self, ctx: commands.Context, search: str):
        wiki = wikipedia(search)
        info_box = ""
        try:
            if not wiki.infobox:
                return await ctx.send("No infobox found")
            for info in wiki.infobox:
                info_box += info
                info_box += "\n"
            if len(info_box) < 2000:
                return await ctx.send("{} \nRead more here: {}".format(info_box, wiki.url))
            else:
                await ctx.send(info_box[0:2000])
                return await ctx.send("Read more here: {}".format(wiki.url))
        except AttributeError:
            return await ctx.send("No articles found")


async def setup(bot):
    await bot.add_cog(Wiki(bot))