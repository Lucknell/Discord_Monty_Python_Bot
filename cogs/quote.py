from discord.ext import commands
import discord
import sys
sys.path.append("/src/bot/cogs/lucknell/")
from quote import quote_finder, InvalidCategoryGiven, QuoteNotFoundError


class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, ctx, category, *, search=None):
        try:
            quote = quote_finder(category, search)
        except QuoteNotFoundError:
            return await ctx.send("No quotes found")
        except InvalidCategoryGiven:
            return await ctx.send("get some $help you gave an invalid category.")
        if len(quote.quote) > 2000:
            await ctx.send(quote.quote[0:2000])
            return await ctx.send(quote.quote_URL)
        else:
            return await ctx.send("{}\n{}".format(quote.quote, quote.quote_URL))

def setup(bot):
    bot.add_cog(Quote(bot))