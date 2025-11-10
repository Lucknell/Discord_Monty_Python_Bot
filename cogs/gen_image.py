import discord
import requests
from pymongo import MongoClient
from discord import app_commands
from discord.ext import commands

class Gen_Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "gen_image", description ="Let's help me take over the world")
    async def gen_image(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.send_message("Adding request to queue. Please wait for your image.")
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = {"user_id": interaction.user.id,
            "server": interaction.guild_id,
            "channel": interaction.channel_id,
            "state": "new",
            "prompt": prompt,
        }
        client["Monty"].gen_image.insert_one(query)
        x = requests.get(f"http://192.168.1.107:5101/checkimagejobs/{interaction.guild.id}")


           
async def setup(bot):
    await bot.add_cog(Gen_Image(bot))