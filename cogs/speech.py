import discord
import random
from discord.ext import commands
from typing import Literal
import cogs.lucknell.utils as utils
from cogs.lucknell.lyrics import lyric_finder, SongNotFoundError

class Speech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name = "say", with_app_command = True, description ="Speak english")
    async def say(self, ctx, speech):
        self.bot.loop.create_task(utils.create_voice_and_play(ctx, speech, self.bot))

    @commands.hybrid_command(name = "sing", with_app_command = True, description ="I get my American Idol on")
    async def sing(self, ctx, song_name):
        self.bot.loop.create_task(self.__sing(ctx, song_name, 17, "genius"))

    @commands.hybrid_command(name = "disconnect", with_app_command = True, description ="Goodbye Tien")
    async def dc(self, ctx):
        await utils.dc(ctx)

    async def __sing(self, ctx, args, lang, provider="azlyrics"):
        # return await ctx.send("This function is disabled")
        msg = await ctx.send("loading...")
        try:
            song = lyric_finder(args, provider)
        except SongNotFoundError:
            return await ctx.send("Song could not be found")
        await msg.edit(content="Sing along here\n{}".format(song.URL))
        await utils.create_voice_and_play(ctx, song.lyrics[0:600], self.bot )

async def setup(bot):
    await bot.add_cog(Speech(bot))