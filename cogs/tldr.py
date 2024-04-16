from discord.ext import commands
import discord
import os
import cogs.lucknell.utils as utils
from newspaper import Article
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest


class Tldr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class GetFlags(commands.FlagConverter):
        url: str = commands.flag(description="New article please")

    @commands.hybrid_command(name = "tldr", with_app_command = True, description ="Obtain a too long did not read")
    async def tldr(self, ctx: commands.Context, flags: GetFlags):
        if not flags.url or not utils.valid_URL(flags.url):
            return await ctx.send("Please provide a valid url")
        msg = await ctx.send("loading...")
        article = Article(flags.url)
        article.download()
        article.parse()
        text = self.summarize(article.text, .06)
        if len(text) > 1:
            await msg.edit(content=(text))
        else:
            await msg.edit(content="unsupported at this time")

    def summarize(self, text, per):
        nlp = spacy.load('en_core_web_sm')
        doc= nlp(text)
        tokens=[token.text for token in doc]
        word_frequencies={}
        for word in doc:
            if word.text.lower() not in list(STOP_WORDS):
                if word.text.lower() not in punctuation:
                    if word.text not in word_frequencies.keys():
                        word_frequencies[word.text] = 1
                    else:
                        word_frequencies[word.text] += 1
        max_frequency=max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word]=word_frequencies[word]/max_frequency
        sentence_tokens= [sent for sent in doc.sents]
        sentence_scores = {}
        for sent in sentence_tokens:
            for word in sent:
                if word.text.lower() in word_frequencies.keys():
                    if sent not in sentence_scores.keys():                            
                        sentence_scores[sent]=word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent]+=word_frequencies[word.text.lower()]
        select_length=int(len(sentence_tokens)*per)
        summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
        final_summary=[word.text for word in summary]
        summary=''.join(final_summary)
        return summary

async def setup(bot):
    await bot.add_cog(Tldr(bot))