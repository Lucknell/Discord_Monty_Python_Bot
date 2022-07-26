from discord.ext import commands
import discord
import sys
import utils
from tweet_vid import tweet_vid, TweetDownloadFailedError
from reddit_vid import reddit_vid, RedditDownloadFailedError
from tik_vid import tik_vid, TikTokDownloadFailedError
import os
#from redvid import Downloader
sys.path.append("/src/bot/cogs/lucknell/")


class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['get'])
    async def download(self, ctx, URL=None):
        if not URL or not utils.valid_URL(URL):
            return await ctx.send("Please provide a valid URL")
        if "v.redd.it" in URL or "reddit.com" in URL:
            return await self.reddit_vid(ctx, URL)
        elif "twitter.com" in URL:
            return await self.twitter_vid(ctx, URL)
        elif "tiktok.com" in URL:
            return await self.tiktok_vid(ctx, URL)
        else:
            return await ctx.send("Unsupported sorry!")

    async def reddit_vid(self, ctx, URL):
        async with ctx.typing():
            try:
                reddit = reddit_vid(URL)
            except RedditDownloadFailedError:
                return await ctx.reply("Could not download that reddit video sorry.")
        await ctx.send(reddit.URL)
    
    async def twitter_vid(self, ctx, URL):
        async with ctx.typing():
            try:
                twitter = tweet_vid(URL)
            except TweetDownloadFailedError:
                return await ctx.reply("Could not download that tweet sorry.")
        await ctx.send(twitter.URL)

    async def tiktok_vid(self, ctx, URL):
        async with ctx.typing():
            try:
                tiktok = tik_vid(URL)
            except TikTokDownloadFailedError:
                await ctx.send("first download failed retrying")
                try:
                    tiktok = tik_vid(URL)
                except TikTokDownloadFailedError:
                    return await ctx.reply("Could not download that tiktok sorry.")
        await ctx.send(tiktok.URL)

def setup(bot):
    bot.add_cog(Download(bot))
