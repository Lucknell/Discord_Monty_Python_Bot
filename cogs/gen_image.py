from discord.ext import commands
import discord
import requests
from pymongo import MongoClient

class Gen_Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "gen_image", with_app_command = True, description ="Let's help me take over the world")
    async def gen_image(self, ctx: commands.Context, prompt: str):
        msg = await ctx.send("Adding request to queue. Please wait for your image.")
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = {"user_id": ctx.author.id,
            "server": ctx.guild.id,
            "channel": ctx.channel.id,
            "message_id": msg.id,
            "state": "new",
            "prompt": prompt,
        }
        client["Monty"].gen_image.insert_one(query)
        x = requests.get(f"http://192.168.1.107:5101/checkimagejobs/{ctx.guild.id}")


           
async def setup(bot):
    await bot.add_cog(Gen_Image(bot))