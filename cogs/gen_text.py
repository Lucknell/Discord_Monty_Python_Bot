from discord.ext import commands
import discord
import logging
from gpt4all import GPT4All
import os
import threading
import asyncio
from typing import Literal
import math
import requests
from pymongo import MongoClient

class Gen_Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#    async def model_autocomplete(interaction: discord.Interaction, current: str,) -> List[commands.Choice[str]]:
#        models = ['mistral', 'wizardlm']
#        return [
#            commands.Choice(name=model, value=model)
#            for model in models if current.lower() in model.lower()
#        ]

    @commands.hybrid_command(name = "askme", with_app_command = True, description ="Let's help me take over the world")
    async def gen_text(self, ctx: commands.Context, prompt: str, model :Literal['mistral', 'wizardlm',"falcon"] ='mistral', temperature: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] = 0):
        temp = temperature/10
        await self.add_ai_job(ctx, prompt, model, temp)
        #threading.Thread(target=self.ai_response, args=(ctx, prompt, message, model, temp)).start()
    
    def ai_response(self, ctx: commands.Context, prompt: str, message, model: str, temperature: float):
        models = {"mistral":"mistral-7b-instruct-v0.1.Q4_0.gguf","wizardlm":"wizardlm-13b-v1.2.Q4_0.gguf","mpt":"mpt-7b-chat-newbpe-q4_0.gguf"}
        self.bot.logger.info(model)
        file_path = f"/src/bot/models/{models[model]}"
        chat_model = GPT4All(file_path)
        with chat_model.chat_session():
            response = chat_model.generate(prompt=prompt, temp=temperature, n_predict=2048)
            embed = discord.Embed()
            if len(response) < 1024:
                embed.add_field(name="‎‎", value=response)
                #self.bot.loop.create_task(message.edit(content=model.current_chat_session[2]["content"]))
                self.bot.loop.create_task(message.edit(content="‎‎",embed=embed))
            else:
                interations = math.ceil(len(response) / 1024)
                for x in range(interations):
                    embed.add_field(name="‎‎", value=response[x*1024:(x+1)*1024])
                self.bot.loop.create_task(message.edit(content="‎‎",embed=embed))

    async def add_ai_job(self, ctx, prompt, model, temperature):
        msg = await ctx.send("Adding request to queue. Please wait for a response.")
        client = MongoClient("mongodb://192.168.1.107:27017/")
        query = {"user_id": ctx.author.id,
            "server": ctx.guild.id,
            "channel": ctx.channel.id,
            "message_id": msg.id,
            "state": "new",
            "question": prompt,
            "model":model,
            "temperature":temperature
        }
        client["Monty"].gen_text.insert_one(query)
        x = requests.get(f"http://192.168.1.107:5101/checkaijobs/{ctx.guild.id}")

async def setup(bot):
    await bot.add_cog(Gen_Text(bot))
