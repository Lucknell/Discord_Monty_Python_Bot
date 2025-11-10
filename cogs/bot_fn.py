import os
import io
import time
import shutil
import random
import discord
import requests
import pytesseract
import numpy as np
from PIL import Image
from cogs.lucknell import utils
from discord.ext import commands
from discord import app_commands
from langchain_ollama import ChatOllama


class Monty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Status report number 2")
    async def status(self, interaction: discord.Interaction):
        statuses = [
            "Jokes on you we still alive",
            "I'm fine, get X go",
            "Systems online awaiting next task",
            "Damage report returned. No damage found",
            "You scared ain't ya?",
        ]
        # randInt is inclusive of the upper bound
        return await interaction.response.send_message(
            statuses[random.randint(0, len(statuses) - 1)]
        )

    @app_commands.command(name="totext", description="convert an image from a URL to text")
    async def totext(self, interaction: discord.Interaction, url: str):
        if not url:
            return await interaction.response.send_message(
                "Try that again but give me a URL to an image next time"
            )
        url = utils.valid_URL(url)
        if not url:
            return await interaction.response.send_message("invalid URL")
        url = url.string
        filename = url.split("/")[-1]
        start = time.time()
        size = 0
        MAX_TIME = 2
        MAX_SIZE = 16 * 1024 * 1024
        chunks = b""
        with requests.get(url, stream=True) as r:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024):
                    if time.time() - start > MAX_TIME:
                        raise ValueError("TIMEOUT")
                    size += len(chunk)
                    chunks += chunk
                    if size > MAX_SIZE:
                        raise ValueError("TOO BIG")
                shutil.copyfileobj(io.BytesIO(chunks), f)

        try:
            img = np.array(Image.open(filename))
        except Image.UnidentifiedImageError:
            os.remove(filename)
            return await interaction.response.send_message("Not an image")
        text = pytesseract.image_to_string(img)
        os.remove(filename)
        await interaction.response.send_message(text)

    @commands.hybrid_command(
        name="good", with_app_command=False, description="Say good bot"
    )
    async def good(self, ctx: commands.Context, word: str):
        if arg.lower() == "bot":
            await ctx.message.add_reaction("😄")

    @commands.hybrid_command(
        name="bad", with_app_command=False, description="Say bad bot"
    )
    async def bad(self, ctx: commands.Context, word: str):
        if arg.lower() == "bot":
            await ctx.send("alright then.")

    @app_commands.command(name="about", description="learn more about me")
    async def about(self, interaction: discord.Interaction):
        return await interaction.response.send_message(
            "You can learn more about me here\nhttps://github.com/Lucknell/Discord_Monty_Python_Bot"
        )


    @app_commands.command(
        name="react", description="This stuff takes some concentration you know..."
    )
    async def reaction(
        self, interaction: discord.Interaction, message_id: str, phrases: str
    ):
        if not message_id or not phrases:
            return await interaction.response.send_message(
                "I need a message id like {} and a phrase like **uncopyrightable**".format(
                    interaction.message.id
                )
            )
        try:
            msg = await interaction.channel.fetch_message(message_id)
        except discord.errors.NotFound:
            return await interaction.response.send_message("invalid id")
        except discord.errors.HTTPException:
            return await interaction.response.send_message("invalid id")
        await interaction.response.send_message("Done.", ephemeral=True)
        letters = []
        emojis = {
            "a": "🇦",
            "b": "🇧",
            "c": "🇨",
            "d": "🇩",
            "e": "🇪",
            "f": "🇫",
            "g": "🇬",
            "h": "🇭",
            "i": "🇮",
            "j": "🇯",
            "k": "🇰",
            "l": "🇱",
            "m": "🇲",
            "n": "🇳",
            "o": "🅾️",
            "p": "🅿️",
            "q": "🇶",
            "r": "🇷",
            "s": "🇸",
            "t": "🇹",
            "u": "🇺",
            "v": "🇻",
            "w": "🇼",
            "x": "🇽",
            "y": "🇾",
            "z": "🇿",
            "#": "#️⃣",
            "0": "0️⃣",
            "1": "1️⃣",
            "2": "2️⃣",
            "3": "3️⃣",
            "4": "4️⃣",
            "5": "5️⃣",
            "6": "6️⃣",
            "7": "7️⃣",
            "8": "8️⃣",
            "9": "9️⃣",
        }
        phrase = phrases.lower().split(" ")
        phrases = "".join(phrase)
        for letter in str(phrases):
            if letter in letters:
                return await interaction.response.send_message(
                    "https://tenor.com/view/invader-zim-movie-enter-the-gif-14899370"
                )
            else:
                letters.append(letter)
        for letter in letters:
            try:
                await msg.add_reaction(emojis[letter])
            except KeyError:
                pass

    @app_commands.command(
        name="smartreact", description="This stuff takes some concentration you know..."
    )
    async def smart_reaction(
        self, interaction: discord.Interaction, message_id: str
    ):
        if not message_id:
            return await interaction.response.send_message(
                "I need a message id like {} and a phrase like **uncopyrightable**".format(
                    interaction.message.id
                )
            )
        # https://discord.com/channels/760693283885416458/760693285072797709/1403276585691512902
        try:
            if "https://" in message_id:
                message_id = message_id.split("/")[-1]
            msg = await interaction.channel.fetch_message(message_id)
        except discord.errors.NotFound:
            return await interaction.response.send_message("invalid id")
        except discord.errors.HTTPException:
            return await interaction.response.send_message("invalid id")
        await interaction.response.send_message("I am cooking up something.", ephemeral=True)
        prompt = f"""
        “You are an emoji translator.  Your task is to analyze a given text
message and generate a response consisting *only* of emojis.  For each
message, produce a CSV output containing only Emojis. The CSV output contains a sequence
of emojis separated by a comma, representing the most appropriate reaction to the ‘Original
Message’.  Do not include any explanations, introductions, or additional
text beyond the emoji response.  Focus solely on the emoji translation.

**Example:**

**Input Message:** “I just won the lottery!”

**Output CSV:**

🎉,🥳,💰,🤩

**Now, take the following message and generate the CSV Emoji response:**

'{msg.content}'.

**Notes for the AI:**

*   Emphasize that the response *must* be only emojis.
*   Specify the CSV format clearly.
*   Provide a clear example to illustrate the desired output.
*   Response MUST contain a comma.
        """
        model = ChatOllama(model="gemma3", base_url="http://192.168.1.107:11434/")
        messages = [
            (
                "system",
                """
                Respond back with only emojis in an array list. Only return the list. Do not wrap the response in a code block
                """,
            ),
            ("human", prompt),
        ]
        response = model.invoke(prompt)
        self.bot.logger.info(response)
        emojis = response.content.split(",")
        self.bot.logger.info(emojis)
        for emoji in emojis:
            try:
                await msg.add_reaction(emoji.strip().lstrip())
            except discord.HTTPException:
                self.bot.logger.error(emoji)
    @app_commands.command(name="flip", description="flip a coin")
    async def flip(self, interaction: discord.Interaction):
        coin = random.randint(0, 1)
        if coin == 1:
            return await interaction.response.send_message("Heads")
        else:
            return await interaction.response.send_message("Tails")
    
    
    

async def setup(bot):
    await bot.add_cog(Monty(bot))
