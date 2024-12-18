from discord.ext import commands
import discord
import sys
import random
sys.path.append("/src/bot/cogs/lucknell/")
from pokemon import pokemon_finder, PokemonNotFoundError

class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "pkmn", with_app_command = True, description ="Get pokemon info")
    async def pokemon(self, ctx: commands.Context, search: str):
        await ctx.defer()
        if not search:
            return await ctx.send("Please give a string to search with")
        try:
            pokemon = pokemon_finder(search)
        except PokemonNotFoundError:
            return await ctx.send("No results found")
        embed = discord.Embed()
        if pokemon.picture:
            embed.set_image(url=pokemon.picture)
        embed.set_author(name=pokemon.heading)
        embed.add_field(name="Type", value=pokemon.type)
        if pokemon.pokedex:
            embed.add_field(name="Pokedex", value=pokemon.pokedex[random.choice(list(pokemon.pokedex.keys()))])
        embed.add_field(name="URL", value=pokemon.URL)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pokemon(bot))