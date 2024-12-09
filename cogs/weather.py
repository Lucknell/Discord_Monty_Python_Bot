from discord.ext import commands
import discord
import requests
import random
import configparser
import sys
import threading
import asyncio
sys.path.append("/src/bot/cogs/lucknell/")
import utils


config = configparser.ConfigParser()
config.read('/src/bot/config.ini')

class Weather(commands.Cog):
    threads = []
    def __init__(self, bot):
        self.bot = bot

    async def _zip(self, ctx, arg=None):
        error_cases = ["https://tenor.com/view/family-guy-ollie-williams-its-raining-side-ways-weatherman-weather-gif-5043009",
                    "https://tenor.com/view/rain-its-gon-rain-weather-report-gif-5516318"]
        # await client.user.edit(username=names[random.randint(0, len(names) - 1)])
        if not arg:
            return await ctx.send(error_cases[random.randint(0, len(error_cases) - 1)])
        API_key = config['openweathermap']['api_key']
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        Final_url = base_url + "appid=" + API_key + "&zip=" + arg
        weather_data = requests.get(Final_url).json()
        # print(weather_data)
        if weather_data["cod"] == "404":
            # await client.user.edit(username=Bot_Name)
            return await ctx.send("invalid zipcode")
        #enhanced_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&appid={}"
        #exclude = "minutely,hourly,daily"
        # enhanced_weather_data = requests.get(enhanced_url.format(
        # weather_data["coord"]["lat"], weather_data["coord"]["lon"], exclude, API_key)).json()
        # print(enhanced_weather_data)
        temp = str(round(utils.KtoF(weather_data["main"]["temp"]), 1))
        feels_like = str(round(utils.KtoF(weather_data["main"]["feels_like"]), 1))
        temp_min = str(round(utils.KtoF(weather_data["main"]["temp_min"]), 1))
        temp_max = str(round(utils.KtoF(weather_data["main"]["temp_max"]), 1))
        humidity = str(weather_data["main"]["humidity"])
        wind_speed = str(weather_data["wind"]["speed"])
        wind_dir = self.wind_degree(weather_data["wind"]["deg"])
        #wind_gust = str(weather_data["wind"]["gust"])
        weather_talk = "Currently the weather for {} is, {} with {}, the temperature is {} degrees Fahrenheit. \
It currently feels like {} degrees Fahrenheit. The low and high are {} and {}. The humidity is at \
{}% with a wind speed of {} mph moving {}. Have a good day {}"
        weather_talk = weather_talk.format(weather_data["name"], weather_data["weather"][0]["main"],
                                        weather_data["weather"][0]["description"], temp, feels_like, temp_min, temp_max,
                                        humidity, wind_speed, wind_dir, (ctx.message.author.nick if ctx.message.author.nick != None else ctx.message.author.name))
        if ctx.message.author.voice:
            await utils.create_voice_and_play(ctx, weather_talk, "en_US/cmu-arctic_low", self.bot)
        else:
            await ctx.send(weather_talk)
        # await client.user.edit(username=Bot_Name)

    @commands.hybrid_command(name = "weather", with_app_command = True, description ="Get the weather for your zip code")
    async def zip(self, ctx: commands.Context, zip: str):
        await self._zip(ctx, zip)
        #x = threading.Thread(target=asyncio.run, args=(self._zip(ctx, arg)), name=ctx.guild.id)
        #x.start()

    def wind_degree(self, int):
        if (int > 345 and int < 361) or (int > -1 and int < 16):
            return "N"
        elif int > 15 and int < 36:
            return "N/NE"
        elif int > 35 and int < 56:
            return "NE"
        elif int > 55 and int < 76:
            return "E/NE"
        elif int > 75 and int < 106:
            return "E"
        elif int > 105 and int < 126:
            return "E/SE"
        elif int > 125 and int < 146:
            return "SE"
        elif int > 145 and int < 166:
            return "S/SE"
        elif int > 165 and int < 196:
            return "S"
        elif int > 195 and int < 216:
            return "S/SW"
        elif int > 215 and int < 236:
            return "SW"
        elif int > 235 and int < 256:
            return "W/SW"
        elif int > 255 and int < 286:
            return "W"
        elif int > 295 and int < 306:
            return "W/NW"
        elif int > 305 and int < 326:
            return "NW"
        elif int > 325 and int < 346:
            return "N/NW"
        else:
            return "You really shouldn't be seeing this..."

async def setup(bot):
    await bot.add_cog(Weather(bot))
