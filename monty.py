import os
import sys
import time
import discord
import logging
import asyncio
import requests
import math

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
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ipc_server = ipc.Server(self, secret_key="theholygrail", host="0.0.0.0", standard_port=8765)

    async def setup_hook(self):
        self.logger = logger
        filepath = "/src/bot/down/"
        if os.path.exists(filepath):
            files = os.listdir(filepath)
            for f in files:
                os.remove(filepath+f)
            os.rmdir(filepath)
        files = os.listdir("/src/bot/cogs/")
        for f in files:
            if f.endswith(".py"):
                await self.load_extension("cogs." + f.replace(".py", ""))
                print(f)
        await self.tree.sync()
        print(f"Synced Slash commands for {self.user}.")

    async def on_ipc_ready(self):
        print("I just wanna talk")
        
    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)
        
    async def on_ready(self):
        #search for jobs that were added before the reboot
        mclient = MongoClient("mongodb://192.168.1.107:27017/")
        jobs = mclient.Monty.downloader.find({"state":"Failed to download"})
        for job in jobs:
            await self.process_failed_jobs(job, mclient)
        jobs = mclient.Monty.downloader.find({"state":"Ready!"})
        for job in jobs:
            await self.process_unposted_jobs(job, mclient)
        guilds = []
        new_jobs = False
        jobs = mclient.Monty.downloader.find({"state":"new"})
        for job in jobs:
            new_jobs = True
            guilds.append(job["server"])
        set_guilds = set(guilds)
        if not new_jobs:
            print("No pending jobs")
        for guild in set_guilds:
            print(guild)
            x = requests.get("http://192.168.1.107:5101/checkjobs/" + str(guild))
            print (x)
        jobs = mclient.Monty.gen_text.find({"state":"new"})
        for job in jobs:
            new_jobs = True
            guilds.append(job["server"])
        set_guilds = set(guilds)
        if not new_jobs:
            print("No pending ai jobs")
        for guild in set_guilds:
            print(guild)
            x = requests.get("http://192.168.1.107:5101/checkaijobs/" + str(guild))
            print (x)
       
    async def on_command_error(self, ctx, error):
        if ctx.interaction:
            await ctx.reply(error, ephemeral = True)
    
    async def process_failed_jobs(self, job, mclient):
            URL = job["URL"]
            user = job["user_id"]
            message = job["message"]
            msg_id = job["message_id"]
            guild = discord.utils.get(client.guilds, id=int(job["server"]))
            channel = discord.utils.get(guild.channels, id=int(job["channel"]))
            msg = await channel.fetch_message(msg_id)
            await msg.edit(content =f"Original url: {URL}\nFailed to download")
            mclient.Monty.downloader.delete_one(job)

    async def process_unposted_jobs(self, job, mclient):
            URL = job["URL"]
            user = job["user_id"]
            message = job["message"]
            msg_id = job["message_id"]
            guild = discord.utils.get(client.guilds, id=int(job["server"]))
            channel = discord.utils.get(guild.channels, id=int(job["channel"]))
            filepath = "/src/bot/down/"+str(job["file"])

            if not os.path.exists(filepath):
                print("file not found starting the process again")
                update = {"$set": {"state":"new"}}
                mclient.Monty.downloader.update_one(job, update)
                x = requests.get("http://192.168.1.107:5101/checkjobs/"+str(job["server"]))

client = Bot(command_prefix = prefix, intents = intents)

@client.hybrid_command(name = "test", with_app_command = True, description = "Hope that this works ")
async def test(ctx: commands.Context, temp: Literal['Hello', 'World']):
    await ctx.reply("It did not.")
    print (temp, "cheese")

avatar_path = "/src/bot/avatar.png"
fp = open(avatar_path, 'rb')
avatar = fp.read()
global logger
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)  # Do not allow DEBUG messages through
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    "{asctime}: {levelname}: {name}: {message}", style="{"))
logger.addHandler(handler)

@client.ipc_server.route()
async def post_jobs(self, data):
    #IPC cannot send data over. we will have to check for the ready state in the table.
    mclient = MongoClient("mongodb://192.168.1.107:27017/")
    path ="/src/bot/down/"
    for i in mclient.Monty.downloader.find({"state":"Ready!"}):
        URL = i["URL"]
        user = i["user_id"]
        message = i["message"]
        msg_id = i["message_id"]
        guild = discord.utils.get(client.guilds, id=int(i["server"]))
        channel = discord.utils.get(guild.channels, id=int(i["channel"]))
        if i["pictures"]:
            try:
                msg = await channel.fetch_message(msg_id)
            except Exception as e:
                print (e)
                mclient.Monty.downloader.delete_one(i)
                continue
            await msg.edit(content =f"Original url: {URL}\n{message}")
            for file in i["file"]:
                if not file.endswith(".jpg"):
                    continue
                await channel.send(file=discord.File(path+file))
                os.remove(path+file)
            mclient.Monty.downloader.delete_one(i)
            continue
        filepath = str(i["file"])
        if not path in filepath:
            filepath = path+str(i["file"])

        if not os.path.exists(filepath):
            print(f"{filepath} file not found starting the process again")
            update = {"$set": {"state":"new"}}
            mclient.Monty.downloader.update_one(i, update)
            x = requests.get("http://192.168.1.107:5101/checkjobs/"+str(i["server"]))
            continue

        if ((os.path.getsize(filepath)/(1024*1024)) <= 8):
            try:
                msg = await channel.fetch_message(msg_id)
            except Exception as e:
                print (e)
                os.remove(filepath)
                mclient.Monty.downloader.delete_one(i)
                continue
            await msg.edit(content =f"Original url: {URL}\n{message}")
            await channel.send(file=discord.File(filepath))
            os.remove(filepath)
        elif ((os.path.getsize(filepath)/(1024*1024)) > 8):
            await channel.send(f"I am sorry <@{user}> that file is getting deleted because it is too large for me to send on discord.\n here is your URL: {URL}")
            os.remove(filepath)
        mclient.Monty.downloader.delete_one(i)
    for i in mclient.Monty.downloader.find({"state":"Failed to download"}):
        await client.process_failed_jobs(i, mclient)
    jobs = False
    for i in mclient.Monty.downloader.find():
        jobs = True
    if not jobs:
        files = os.listdir(path)
        for f in files:
            os.remove(path + f)
            print(f"deleting {f}")
    return "something cool"


@client.ipc_server.route()
async def post_ai_jobs(self, data):
    #IPC cannot send data over. we will have to check for the ready state in the table.
    mclient = MongoClient("mongodb://192.168.1.107:27017/")
    for i in mclient.Monty.gen_text.find({"state":"Ready!"}):
        user = i["user_id"]
        response = i["answer"]
        msg_id = i["message_id"]
        guild = discord.utils.get(client.guilds, id=int(i["server"]))
        channel = discord.utils.get(guild.channels, id=int(i["channel"]))
        try:
            msg = await channel.fetch_message(msg_id)
        except Exception as e:
            print (e)
            mclient.Monty.gen_text.delete_one(i)
            continue
        embed = discord.Embed()
        if len(response) < 1024:
                embed.add_field(name="‎‎", value=response)
                await msg.edit(content="‎‎",embed=embed)
        else:
            interations = math.ceil(len(response) / 1024)
            for x in range(interations):
                embed.add_field(name="‎‎", value=response[x*1024:(x+1)*1024])
            await msg.edit(content="‎‎",embed=embed)
        mclient.Monty.gen_text.delete_one(i)
    return "something ai"

@client.ipc_server.route()
async def get_guild_count(self, data):
    return len(client.guilds)

@client.ipc_server.route()
async def get_guild_idss(self, data):
    final = []
    for guild in client.guilds:
        final.append(guild.id)
    return final

@client.ipc_server.route()
async def get_guild(self, data):
    guild = client.get_guild(data.guild_id)
    if guild is None: return None

    guild_data = {
        "name": guild.name,
        "id": guild.id,
        "prefix": "$"
    }

    return guild_data

async def main():
    async with client:
        await client.ipc_server.start()
        print("Starting bot")
        await client.start(os.getenv('TOKEN'))

asyncio.run(main())
