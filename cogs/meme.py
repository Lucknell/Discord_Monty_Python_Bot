from discord.ext import commands
import discord
import sys
from PIL import Image
from PIL import ImageDraw
from io import BytesIO
import requests
import re
import emoji

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "meme", with_app_command = True, description ="Let's make a meme")
    async def meme(self, ctx: commands.Context, phrase: str):
        img = Image.open("meme/meme.png")
        I1 = ImageDraw.Draw(img)
        I1.text((22, 64), phrase, fill=(255, 255, 255))
        img.save("memed.png")
        await ctx.send(file=discord.File("memed.png"))

    @commands.hybrid_command(name = "missing", with_app_command = True, description ="Let's make a meme")
    async def missing(self, ctx: commands.Context, user: discord.Member = None):
        if not user:
            user = ctx.author
        img = Image.open("meme/lost.jpg")
        asset = user.display_avatar.url
        response = requests.get(asset)
        data = BytesIO(response.content)
        pfp = Image.open(data)
        pfp = pfp.resize((158,116))
        img.paste(pfp, (72,88))
        I1 = ImageDraw.Draw(img)
        name = emoji.replace_emoji(user.display_name)
        I1.text((134, 214), name, fill=(0, 0, 0))
        img.save("missing.jpg")
        await ctx.send(file=discord.File("missing.jpg"))

async def setup(bot):
    await bot.add_cog(Meme(bot))
