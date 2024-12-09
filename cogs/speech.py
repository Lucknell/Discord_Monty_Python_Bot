import discord
import random
from discord.ext import commands
from typing import Literal
import cogs.lucknell.utils as utils
from cogs.lucknell.lyrics import lyric_finder, SongNotFoundError

class Speech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name = "say", with_app_command = True, description ="Speak english")
    async def say(self, ctx, speech, language: Literal["বাংলা (Bengali)","Deutsch (German)","Ελληνικά (Greek)","English","English US",
        "Español (Spanish)", "فارسی (Persian)","Suomi (Finnish)","Français (French)","ગુજરાતી (Gujarati)","Hausa","Magyar Nyelv (Hungarian)",
        "Italiano (Italian)","Basa Jawa (Javanese)","한국어 (Korean)","नेपाली (Nepali)","Nederlands (Dutch)","Polski (Polish)","Русский (Russian)",
        "Kiswahili","తెలుగు (Telugu)","Setswana","украї́нська мо́ва (Ukrainian)","Tiếng Việt (Vietnamese)"]):
        language_packs = {"বাংলা (Bengali)":"bn/multi_low",
            "Deutsch (German)":"de_DE/m-ailabs_low",
            "Ελληνικά (Greek)":"el_GR/rapunzelina_low",
            "English":"en_UK/apope_low",
            "English US":"en_US/cmu-arctic_low",
            "Español (Spanish)":"es_ES/carlfm_low",
            "فارسی (Persian)":"fa/haaniye_low",
            "Suomi (Finnish)":"fi_FI/harri-tapani-ylilammi_low",
            "Français (French)":"fr_FR/m-ailabs_low",
            "ગુજરાતી (Gujarati)":"gu_IN/cmu-indic_low",
            "Hausa":"ha_NE/openbible_low",
            "Magyar Nyelv (Hungarian)":"hu_HU/diana-majlinger_low",
            "Italiano (Italian)":"it_IT/mls_low",
            "Basa Jawa (Javanese)":"jv_ID/google-gmu_low",
            "한국어 (Korean)":"ko_KO/kss_low",
            "नेपाली (Nepali)":"ne_NP/ne-google_low",
            "Nederlands (Dutch)":"nl/bart-de-leeuw_low",
            "Polski (Polish)":"pl_PL/m-ailabs_low",
            "Русский (Russian)":"ru_RU/multi_low",
            "Kiswahili":"sw/lanfrica_low",
            "తెలుగు (Telugu)":"te_IN/cmu-indic_low",
            "Setswana":"tn_ZA/google-nwu_low",
            "украї́нська мо́ва (Ukrainian)":"uk_UK/m-ailabs_low",
            "Tiếng Việt (Vietnamese)":"vi_VN/vais1000_low"
    }
        self.bot.loop.create_task(utils.create_voice_and_play(ctx, speech, language_packs[language], self.bot))

    @commands.hybrid_command(name = "sing", with_app_command = True, description ="I get my American Idol on")
    async def sing(self, ctx, song_name):
        self.bot.loop.create_task(self.__sing(ctx, song_name, 17, "genius"))

    @commands.hybrid_command(name = "disconnect", with_app_command = True, description ="Goodbye Tien")
    async def dc(self, ctx):
        await utils.dc(ctx)

    async def __sing(self, ctx, args, lang, provider="azlyrics"):
        # return await ctx.send("This function is disabled")
        msg = await ctx.send("loading...")
        try:
            song = lyric_finder(args, provider)
        except SongNotFoundError:
            return await ctx.send("Song could not be found")
        await msg.edit(content="Sing along here\n{}".format(song.URL))
        await utils.create_voice_and_play(ctx, song.lyrics[0:600], "en_US/cmu-arctic_low", self.bot )

async def setup(bot):
    await bot.add_cog(Speech(bot))