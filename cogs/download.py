from discord.ext import commands
import discord
import os
import requests
from pymongo import MongoClient
import cogs.lucknell.utils as utils


class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class GetFlags(commands.FlagConverter):
        url: str = commands.flag(description="Instagram/Tiktok/Reddit/Twitter videos are supported")
        msg: str = commands.flag(default="", description="Message to be sent with a successful upload of the video")

    @commands.hybrid_command(name = "get", with_app_command = True, description ="download a video")
    async def download(self, ctx: commands.Context, flags: GetFlags):
        if not flags.url or not utils.valid_URL(flags.url):
            return await ctx.send("Please provide a valid url")
        return await self.add_url(ctx, flags.url, flags.msg)

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

    async def add_url(self, ctx, URL, message):
        msg = await ctx.send("Added to queue for download. Please wait for file")
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = { "URL": URL,
            "user_id": ctx.author.id,
            "server": ctx.guild.id,
            "channel": ctx.channel.id,
            "message_id": msg.id,
            "state": "new",
            "file": "No file",
            "message": message
        }
        if "instagram.com" in URL:
            client.Monty.insta_downloader.insert_one(query)
            x = requests.get("http://192.168.1.107:5101/check_insta_jobs/"+str(ctx.guild.id))
            return
        client["Monty"].downloader.insert_one(query)
        x = requests.get("http://192.168.1.107:5101/checkjobs/"+str(ctx.guild.id))
    

async def setup(bot):
    await bot.add_cog(Download(bot))
