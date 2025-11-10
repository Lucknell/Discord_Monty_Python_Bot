from discord.ext import commands
import discord
from cogs.lucknell.movies import Movie_Finder, MovieNotFoundError
from discord import app_commands
from langchain_ollama import ChatOllama
import requests
from pymongo import MongoClient
import datetime


class Movies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="movies", with_app_command=True, description="Get Movies info"
    )
    async def Movies(self, ctx: commands.Context):
        await ctx.defer()
        try:
            Movies = Movie_Finder()
        except MovieNotFoundError:
            return await ctx.send("No results found")
        embed = discord.Embed()
        # embed.set_author(name=Movies.heading)
        # embed.add_field(name="Type", value=Movies.type)
        # self, title, release_date, poster, trailer, rating, runtime
        embeds = list()
        for i, (title, params) in enumerate(Movies.movies.items()):
            if i % 25 == 0 and i != 0:
                # We got the 26th element. Make a new embed. 
                embeds.append(embed)
                embed = discord.Embed()
            month, day, year = params.release_date.split()[0].split('/')
            date = self.onDay(datetime.datetime(int(year), int(month), int(day)), 1)
            value = f"Release Date: {params.release_date}\nFollowing Tuesday: {date.month}/{date.day}/{date.year}\nTrailer: {params.trailer}\nRating:{params.rating}\nRuntime:{params.runtime}"
            embed.add_field(name=title, value=value)
        embeds.append(embed)
        for embed in embeds:
            await ctx.send(embed=embed)

    def onDay(self, date, day):
        days = (day - date.weekday() + 7) % 7
        return date + datetime.timedelta(days=days)

async def setup(bot):
    await bot.add_cog(Movies(bot))
