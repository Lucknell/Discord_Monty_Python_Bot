import requests
from typing import Literal
from pymongo import MongoClient
from discord.ext import commands

class Gen_Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# dolphin-mistral:latest    5dc8c5a2be65    4.1 GB    8 minutes ago     
# llama2-uncensored:7b      44040b922233    3.8 GB    17 minutes ago    
# deepseek-r1:7b            0a8c26691023    4.7 GB    40 minutes ago    
# deepseek-r1:1.5b          a42b25d8c10a    1.1 GB    48 minutes ago    
# llama3.2:1b               baf6a787fdff    1.3 GB    2 days ago     
    @commands.hybrid_command(name = "askmonty", with_app_command = True, description ="Let's help me take over the world")
    async def gen_text(self, ctx: commands.Context, prompt: str, model :Literal['dolphin-mistral', 'llama2-uncensored:7b', "deepseek-r1:7b", "deepseek-r1:1.5b", "llama3.2:1b", "gemma3"] = "llama3.2:1b"):
        msg = await ctx.send("Adding request to queue. Please wait for a response.")
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = {"user_id": ctx.author.id,
            "server": ctx.guild.id,
            "channel": ctx.channel.id,
            "message_id": msg.id,
            "state": "new",
            "question": prompt,
            "model":model,
        }
        client["Monty"].gen_text.insert_one(query)
        requests.get(f"http://192.168.1.107:5101/checkaijobs/{ctx.guild.id}")
    
async def setup(bot):
    await bot.add_cog(Gen_Text(bot))
