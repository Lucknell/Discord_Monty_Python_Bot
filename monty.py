import os
import sys
import time
import discord
import logging
import asyncio
import requests
import math
import shutil

from typing import Literal
from datetime import datetime
from discord.utils import find
from pymongo import MongoClient
from discord import app_commands
from discord.ext import commands, ipc

Bot_Name = "Monty Python"
prefix = "$"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ipc_server = ipc.Server(
            self, secret_key="theholygrail", host="0.0.0.0", standard_port=8765
        )

    async def setup_hook(self):
        self.logger = logger
        filepath = "/src/bot/down/"
        if os.path.exists(filepath):
            files = os.listdir(filepath)
            for f in files:
                os.remove(os.path.join(filepath, f))
            os.rmdir(filepath)
        files = os.listdir("/src/bot/cogs/")
        print(files)
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == ".py":
                await self.load_extension(f"cogs.{name}")
                print(name)
        await self.tree.sync()
        print(f"Synced Slash commands for {self.user}.")

    async def on_ipc_ready(self):
        print("I just wanna talk")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)

    async def init_jobs(self, mclient, api):
        jobs = mclient.find({"state": "Failed"})
        for job in jobs:
            await self.process_failed_jobs(job, mclient)
        jobs = mclient.find({"state": "Ready!"})
        for job in jobs:
            await self.process_unposted_jobs(job, mclient, api)

    async def on_ready(self):
        # search for jobs that were added before the reboot
        mclient = MongoClient("mongodb://192.168.1.107:27017/")
        await self.init_jobs(mclient.Monty.downloader, "checkjobs")
        await self.init_jobs(mclient.Monty.insta_downloader, "check_insta_jobs")
        guilds = []
        new_jobs = False
        for job in mclient.Monty.downloader.find({"state": "new"}):
            new_jobs = True
            guilds.append(job["server"])
        set_guilds = set(guilds)
        if not new_jobs:
            print("No pending jobs")
        for guild in set_guilds:
            print(guild)
            x = requests.get(f"http://192.168.1.107:5101/checkjobs/{guild}")
            print(x)
        for job in mclient.Monty.gen_text.find({"state": "new"}):
            new_jobs = True
            guilds.append(job["server"])
        set_guilds = set(guilds)
        if not new_jobs:
            print("No pending ai jobs")
        for guild in set_guilds:
            print(guild)
            x = requests.get(f"http://192.168.1.107:5101/checkaijobs/{guild}")
            print(x)
        for job in mclient.Monty.gen_image.find({"state": "new"}):
            new_jobs = True
            guilds.append(job["server"])
        set_guilds = set(guilds)
        if not new_jobs:
            print("No pending image jobs")
        for guild in set_guilds:
            print(guild)
            x = requests.get(f"http://192.168.1.107:5101/checkimagejobs/{guild}")
            print(x)

    async def on_command_error(self, ctx, error):
        if ctx.interaction:
            await ctx.reply(error, ephemeral=True)

    async def process_failed_jobs(self, job, mclient):
        URL = job["URL"]
        user = job["user_id"]
        message = job["message"]
        msg_id = job["message_id"]
        reason = job["reason"]
        guild = discord.utils.get(client.guilds, id=int(job["server"]))
        channel = discord.utils.get(guild.channels, id=int(job["channel"]))
        msg = await channel.fetch_message(msg_id)
        await msg.edit(content=f"Original url: {URL}\nFailed:{reason}")
        mclient.delete_one(job)

    async def process_unposted_jobs(self, job, mclient, api):
        URL = job["URL"]
        user = job["user_id"]
        message = job["message"]
        msg_id = job["message_id"]
        guild = discord.utils.get(client.guilds, id=int(job["server"]))
        channel = discord.utils.get(guild.channels, id=int(job["channel"]))
        filepath = os.path.join("/src/bot/down/", str(job["file"]))

        if not os.path.exists(filepath):
            print("file not found starting the process again")
            update = {"$set": {"state": "new"}}
            mclient.update_one(job, update)
            x = requests.get(f"http://192.168.1.107:5101/{api}/{job["server"]}")


client = Bot(command_prefix=prefix, intents=intents)


@client.hybrid_command(
    name="test", with_app_command=True, description="Hope that this works "
)
async def test(ctx: commands.Context, temp: Literal["Hello", "World"]):
    await ctx.reply("It did not.")
    print(temp, "cheese")


avatar_path = "/src/bot/avatar.png"
fp = open(avatar_path, "rb")
avatar = fp.read()
global logger
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)  # Do not allow DEBUG messages through
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("{asctime}: {levelname}: {name}: {message}", style="{")
)
logger.addHandler(handler)


async def post_jobs_callback(data, mclient, api):
    for job in mclient.find({"state": "Ready!"}):
        URL = job["URL"]
        user = job["user_id"]
        message = job["message"]
        msg_id = job["message_id"]
        guild = discord.utils.get(client.guilds, id=int(job["server"]))
        channel = discord.utils.get(guild.channels, id=int(job["channel"]))
        print(job)
        if isinstance(job["file"], list):
            try:
                msg = await channel.fetch_message(msg_id)
            except Exception as e:
                print(e)
                mclient.delete_one(job)
                continue
            await msg.edit(content=f"Original url: {URL}\n{message}")
            for file in job["file"]:
                file_path = os.path.join(job["path"], file)
                if (os.path.getsize(file_path) / (1024 * 1024)) > 8:
                    await channel.send(
                        f"I am sorry <@{user}> that file is getting deleted because it is too large for me to send on discord.\n here is your URL: {URL}"
                    )
                    os.remove(filepath)
                    mclient.delete_one(job)
                    continue
                try:
                    msg = await channel.fetch_message(msg_id)
                except Exception as e:
                    print(e)
                    os.remove(file_path)
                    mclient.delete_one(job)
                    continue
                await msg.edit(content=f"Original url: {URL}\n{message}")
                await channel.send(file=discord.File(file_path))
                os.remove(file_path)
            mclient.delete_one(job)
            continue
        if not os.path.exists(filepath):
            print(f"{filepath} file not found starting the process again")
            update = {"$set": {"state": "new"}}
            mclient.update_one(job, update)
            x = requests.get(f"http://192.168.1.107:5101/{api}/{job["server"]}")
            continue
    for job in mclient.find({"state": "Failed"}):
        await client.process_failed_jobs(job, mclient)
    jobs = False
    for job in mclient.find():
        jobs = True
    path = "/src/bot/down/"
    if not jobs:
        files = os.listdir(path)
        for f in files:
            dir_path = os.path.join(path, f)
            print(f"deleting {f}")
            shutil.rmtree(dir_path)
    return "something cool"


@client.ipc_server.route()
async def post_jobs(self, data):
    # IPC cannot send data over. we will have to check for the ready state in the table.
    mclient = MongoClient("mongodb://192.168.1.107:27017/")
    return await post_jobs_callback(data, mclient.Monty.downloader, "checkjobs")


@client.ipc_server.route()
async def post_insta_jobs(self, data):
    # IPC cannot send data over. we will have to check for the ready state in the table.
    mclient = MongoClient("mongodb://192.168.1.107:27017/")
    return await post_jobs_callback(
        data, mclient.Monty.insta_downloader, "check_insta_jobs"
    )


@client.ipc_server.route()
async def post_ai_jobs(self, data):
    # IPC cannot send data over. we will have to check for the ready state in the table.
    mclient = MongoClient("mongodb://192.168.1.107:27017/")
    for job in mclient.Monty.gen_text.find({"state": "Ready!"}):
        user = job["user_id"]
        response = job["answer"]
        msg_id = job["message_id"]
        guild = discord.utils.get(client.guilds, id=int(job["server"]))
        channel = discord.utils.get(guild.channels, id=int(job["channel"]))
        try:
            msg = await channel.fetch_message(msg_id)
        except Exception as e:
            print(e)
            mclient.Monty.gen_text.delete_one(job)
            continue
        embed = discord.Embed()
        if len(response) < 1024:
            embed.add_field(name="‎‎", value=response)
            await msg.edit(content="‎‎", embed=embed)
        else:
            interations = math.ceil(len(response) / 1024)
            for x in range(interations):
                embed.add_field(name="‎‎", value=response[x * 1024 : (x + 1) * 1024])
            await msg.edit(content="‎‎", embed=embed)
        mclient.Monty.gen_text.delete_one(job)
    return "something ai"


@client.ipc_server.route()
async def post_image_jobs(self, data):
    # IPC cannot send data over. we will have to check for the ready state in the table.
    mclient = MongoClient("mongodb://192.168.1.107:27017/")
    for job in mclient.Monty.gen_image.find({"state": "Ready!"}):
        user = job["user_id"]
        file = job["file"]
        msg_id = job["message_id"]
        guild = discord.utils.get(client.guilds, id=int(job["server"]))
        channel = discord.utils.get(guild.channels, id=int(job["channel"]))
        try:
            msg = await channel.fetch_message(msg_id)
        except Exception as e:
            print(e)
            mclient.Monty.gen_image.delete_one(job)
            os.remove(file)
            continue
        await msg.edit(content=f"Your image is ready <@{user}>")
        await channel.send(file=discord.File(file))
        mclient.Monty.gen_image.delete_one(job)
        os.remove(file)
    return "something image"


@client.ipc_server.route()
async def get_guild_count(self, data):
    return len(client.guilds)


@client.ipc_server.route()
async def get_guild_idss(self, data):
    final = [guild.id for guild in client.guilds]
    return final


@client.ipc_server.route()
async def get_guild(self, data):
    guild = client.get_guild(data.guild_id)
    if guild is None:
        return None
    guild_data = {"name": guild.name, "id": guild.id, "prefix": "$"}
    return guild_data


async def main():
    async with client:
        await client.ipc_server.start()
        print("Starting bot")
        await client.start(os.getenv("TOKEN"))


asyncio.run(main())
