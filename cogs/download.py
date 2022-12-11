from discord.ext import commands
import discord
import sys
from tweet_vid import tweet_vid, TweetDownloadFailedError
import os
import requests
#from redvid import Downloader
from pymongo import MongoClient
sys.path.append("/src/bot/cogs/lucknell/")
import utils


class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class GetFlags(commands.FlagConverter):
        url: str = commands.flag(description="Instagram/Tiktok/Reddit/Twitter videos are supported")
        msg: str = commands.flag(default="", description="Message to be sent with a successful upload of the video")

    #@commands.hybrid_command(name = "trouble", with_app_command = True, description="I could destroy the whole world with this one")
    #async def bigbang(self, ctx: commands.Context):
    #    msg1 = await ctx.send("This is a test")
    #    guild = discord.utils.get(self.bot.guilds, id=int(ctx.guild.id))
    #    channel = discord.utils.get(guild.channels, id=int(ctx.channel.id))
    #    msg = await channel.fetch_message(msg1.id)
    #    await msg.edit(content="This was a test")

    @commands.hybrid_command(name = "get", with_app_command = True, description ="download a video")
    #@commands.describe(url="Instagram/Tiktok/Reddit/Twitter videos are supported")
    async def download(self, ctx: commands.Context, flags: GetFlags):
        if not flags.url or not utils.valid_URL(flags.url):
            return await ctx.send("Please provide a valid url")
        if "v.redd.it" in flags.url or "reddit.com" in flags.url:
            return await self.reddit_vid(ctx, flags.url, flags.msg)
        elif "twitter.com" in flags.url:
            return await self.twitter_vid(ctx, flags.url, flags.msg)
        elif "tiktok.com" in flags.url:
            return await self.tiktok_vid(ctx, flags.url, flags.msg)
        elif "instagram.com" in flags.url:
            return await self.insta_vid(ctx, flags.url, flags.msg)
        else:
            return await ctx.send("Unsupported sorry!")

    @commands.hybrid_command(name = "queue", with_app_command = True, description = "check for jobs currently pending")
    async def queue(self, ctx: commands.Context):
        client = MongoClient("mongodb://192.168.1.107:27017/")
        result =""
        new_jobs = False
        jobs = client.Monty.downloader.find({"server":ctx.guild.id})
        for job in jobs:
            new_jobs = True
            result += str(job) +"\n"
        await ctx.send(result if new_jobs else "Nothing is currently in the queue")

    async def reddit_vid(self, ctx, URL, message):
        async with ctx.typing():
            return await self.add_url(ctx, URL, message)

    async def twitter_vid(self, ctx, URL, message):
        async with ctx.typing():
            try:
                twitter = tweet_vid(URL)
            except TweetDownloadFailedError:
                return await ctx.reply("Could not download that tweet sorry.")
        return await ctx.send(f"{message} {twitter.URL}")

    async def tiktok_vid(self, ctx, URL, message):
        async with ctx.typing():
            return await self.add_url(ctx, URL, message)

    async def insta_vid(self, ctx, URL, message):
            async with ctx.typing():
                return await self.add_url(ctx, URL, message)

    async def add_url(self, ctx, URL, message):
        msg = await ctx.send("Added to queue for download. Please wait for file")
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = { "URL": URL,
            "user_id": ctx.author.id,
            "server": ctx.guild.id,
            "channel": ctx.channel.id,
            "message_id": msg.id,
            "state": "new",
            "file": "failed",
            "message": message
        }
        client["Monty"].downloader.insert_one(query)
        x = requests.get("http://192.168.1.107:5101/checkjobs/"+str(ctx.guild.id))
    

async def setup(bot):
    await bot.add_cog(Download(bot))
