import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from cogs.lucknell import utils
from cogs.lucknell.cities.oakland import Oakland
from cogs.lucknell.cities.san_jose import SanJose
from cogs.lucknell.cities.palo_alto import PaloAlto
from cogs.lucknell.cities.sunnyvale import Sunnyvale
from cogs.lucknell.cities.sf_cheap_fun import SFCheapFun
from cogs.lucknell.cities.mountain_view import MountainView


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="events", description="Get Bay Area event info")
    async def Events(self, interaction: discord.Interaction):
        #await interaction.response.defer()
        view = discord.ui.View()
        sites = [
            "SF Cheap Fun",
            "Mountain View",
            "Palo Alto",
            "Sunnyvale",
            "Oakland",
            "San Jose",
        ]
        list_of_options = list()
        for site in sites:
            list_of_options.append(discord.SelectOption(label=site, value=site))
        view.add_item(
            item=discord.ui.Select(options=list_of_options, custom_id="Sites")
        )
        await interaction.response.send_message("Which city?", view=view)
        try:
            msg = await self.bot.wait_for(
                "interaction",
                check=utils.check_select_interaction(interaction.user),
                timeout=60,
            )
        except asyncio.TimeoutError:
            return await interaction.channel.send("Nothing selected.")
        events = None
        for item in view.children:
            index = view.children.index(item)
            view.children[index].disabled = True
            if msg and "Sites" == msg.data["custom_id"]:
                selection = item.values[0]
                item.placeholder = selection
                if selection == "SF Cheap Fun":
                    city = SFCheapFun()
                elif selection == "Mountain View":
                    city = MountainView()
                elif selection == "Palo Alto":
                    city = PaloAlto()
                elif selection == "Sunnyvale":
                    city = Sunnyvale()
                elif selection == "Oakland":
                    city = Oakland()
                elif selection == "San Jose":
                    city = SanJose()
                else:
                    return
                events = city.get_events()
        embed = discord.Embed()
        content = ""
        fields = [
            "Cost: ",
            "\nLocation: ",
            "\nStart time: ",
            "\nEnd time: ",
            "\nLink: ",
        ]
        embeds = list()
        for i, event in enumerate(events):
            if i % 25 == 0 and i != 0:
                # We got an element divisible by 26th element. ship the embed and make a new one
                embeds.append(embed)
                embed = discord.Embed()
            values = [
                event.cost,
                event.location,
                event.start_time,
                event.end_time,
                event.link,
            ]
            value = "".join([x + y for x, y in zip(fields, values) if y is not None])
            # value = f"Cost: {event.cost}\n Location: {event.location} \n Start time: {event.start_time}\n End time: {event.end_time}\nLink:{event.link}"
            embed.add_field(name=event.name, value=value)

        if not events:
            embed = None
            content = "events api broke try again"

        if embeds:
            # We have to multisend now and catch the remaining.
            embeds.append(embed)
            await interaction.channel.send(content=content, embed=embeds[0], view=view)
            for embed in embeds[1:]:
                await interaction.channel.send(embed=embed)
        else:
            await interaction.channel.send(content=content, embed=embed, view=view)


async def setup(bot):
    """Add the command to the bot"""
    await bot.add_cog(Events(bot))