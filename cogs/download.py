import discord
import requests

from cogs.lucknell import utils
from pymongo import MongoClient
from discord import app_commands
from discord.ext import commands


class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="get", description="Download a video and share it here")
    @app_commands.describe(url="Instagram/Tiktok/Reddit/Twitter videos are supported")
    @app_commands.describe(
        msg="Message to be sent with a successful upload of the video"
    )
    async def download(
        self,
        interaction: discord.Interaction,
        url: str,
        msg: str = "",
        summarize: bool = False,
        instructions: str = None,
    ):
        bot_member = interaction.channel.guild.me
        # Get the permissions of the bot in that specific channel
        permissions = interaction.channel.permissions_for(bot_member)

        if not permissions.send_messages:
            return await interaction.response.send_message(
                "I cannot post here. Ignoring request. LOL I sent a message anyway"
            )
        if not url or not utils.valid_URL(url):
            return await interaction.response.send_message("Please provide a valid url")
        return await self.add_url(interaction, url, msg, summarize, instructions)

    @app_commands.command(
        name="queue",
        description="check for jobs currently pending",
    )
    async def queue(self, interaction: discord.Interaction):
        client = MongoClient("mongodb://192.168.1.107:27017/")
        jobs = client.Monty.downloader.find({"server": interaction.guild_id})
        embed = discord.Embed()
        output = [str(job) for job in jobs]
        self.bot.logger.info(output)
        embed.add_field(
            name="**Download Jobs**",
            value="\n".join(output) if output else "Nothing in queue",
        )
        jobs = client.Monty.gen_text.find({"server": interaction.guild_id})
        output = [str(job) for job in jobs]
        self.bot.logger.info(output)
        embed.add_field(
            name="**Gen text Jobs**",
            value="\n".join(output) if output else "Nothing in queue",
        )
        jobs = client.Monty.gen_image.find({"server": interaction.guild_id})
        output = [str(job) for job in jobs]
        self.bot.logger.info(output)
        embed.add_field(
            name="**Gen image Jobs**",
            value="\n".join(output) if output else "Nothing in queue",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="remove_job",
        description="delete a currently pending job for jobs currently pending",
    )
    async def delete_job(self, interaction: discord.Interaction, user_id: str):
        client = MongoClient("mongodb://192.168.1.107:27017/")
        jobs = client.Monty.downloader.find(
            {"server": interaction.guild_id, "user_id": int(user_id)}
        )
        for job in jobs:
            client.Monty.downloader.delete_one(job)
            requests.get(f"http://192.168.1.107:5101/checkjobs/{interaction.guild_id}")
            return await interaction.response.send_message("Deleted download job")
        jobs = client.Monty.gen_text.find(
            {"server": interaction.guild_id, "user_id": int(user_id)}
        )
        for job in jobs:
            client.Monty.gen_text.delete_one(job)
            requests.get(
                f"http://192.168.1.107:5101/checkaijobs/{interaction.guild_id}"
            )
            return await interaction.response.send_message("Deleted gen text job")
        jobs = client.Monty.gen_image.find(
            {"server": interaction.guild_id, "user_id": int(user_id)}
        )
        for job in jobs:
            client.Monty.gen_image.delete_one(job)
            requests.get(
                f"http://192.168.1.107:5101/checkimagejobs/{interaction.guild_id}"
            )
            return await interaction.response.send_message("Deleted imagine job")
        return await interaction.response.send_message("Message not found.")

    async def add_url(self, interaction, URL, message, summarize, instructions):
        summary = (
            "\nSummaries may take more than 10 minutes to post." if summarize else ""
        )
        await interaction.response.send_message(
            f"Added to queue for download. Please wait for completion.{summary}"
        )
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = {
            "URL": URL,
            "user_id": interaction.user.id,
            "server": interaction.guild_id,
            "channel": interaction.channel_id,
            "state": "new",
            "file": "No file",
            "message": message,
            "summarize": summarize,
            "instructions": instructions,
        }
        client["Monty"].downloader.insert_one(query)
        requests.get(f"http://localhost:5102/downloadvideos/{interaction.guild_id}")
        #requests.get(f"http://192.168.1.107:5101/checkjobs/{interaction.guild_id}")

    @app_commands.command(name="test", description="Hope that this works ")
    async def test(self, interaction: discord.Interaction, url:str, summary: bool):
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = {
            "URL": url,
            "user_id": interaction.user.id,
            "server": interaction.guild_id,
            "channel": interaction.channel_id,
            "state": "new",
            "file": "No file",
            "message": None,
            "summarize": summary,
            "instructions": None,
        }
        client["Monty"].downloader.insert_one(query)
        await interaction.response.send_message("Testing the golang backend. I hope it works")
        requests.get(f"http://localhost:5102/downloadvideos/{interaction.guild_id}")

async def setup(bot):
    await bot.add_cog(Download(bot))
