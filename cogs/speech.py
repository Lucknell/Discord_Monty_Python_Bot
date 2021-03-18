from discord.ext import commands
import discord
import sys
import random
sys.path.append("/src/bot/cogs/lucknell/")
import utils
from lyrics import lyric_finder, SongNotFoundError

class Speech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx):
        await utils.TTStime(ctx, "say", 17, self.bot)


    @commands.command()
    async def speak(self, ctx, multipier=None, *, speech=None):
        if not multipier or not speech:
            return
        await utils.TTStime(ctx, "", 10, self.bot, speech, multipier)


    @commands.command()
    async def skazat(self, ctx):
        await utils.TTStime(ctx, "skazat", 54, self.bot)


    @commands.command()
    async def hablar(self, ctx):
        await utils.TTStime(ctx, "hablar", 18, self.bot)


    @commands.command()
    async def parler(self, ctx):
        await utils.TTStime(ctx, "parler", 24, self.bot)


    @commands.command()
    async def dire(self, ctx):
        await utils.TTStime(ctx, "dire", 34, self.bot)


    @commands.command()
    async def hanasu(self, ctx):
        await utils.TTStime(ctx, "hanasu", 39, self.bot)

    @commands.command(aliases=['disconnect', 'leave'])
    async def dc(self, ctx):
        await utils.dc(ctx)

    @commands.command()
    @commands.has_role('Monty\'s keeper')
    async def skip(self, ctx):
        await utils.skip(ctx)

    @commands.command()
    async def sing(self, ctx, *, args):
        await self.__sing(ctx, args, 17)


    @commands.command()
    async def canta(self, ctx, *, args):
        await self.__sing(ctx, args, 18)


    @commands.command()
    async def sing_genius(self, ctx, *, args):
        await self.__sing(ctx, args, 17, "genius")


    async def __sing(self, ctx, args, lang, provider="azlyrics"):
        # return await ctx.send("This function is disabled")
        try:
            song = lyric_finder(args, provider)
        except SongNotFoundError:
            return await ctx.send("Song could not be found")
        await ctx.send("Sing along here\n{}".format(song.URL))
        await utils.TTStime(ctx, "", lang, self.bot, song.lyrics[0:850], name=str(random.randint(0, 10000)))


def setup(bot):
    bot.add_cog(Speech(bot))