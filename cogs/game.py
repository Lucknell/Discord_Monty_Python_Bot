
from discord.ext import commands
import discord
import sys
import random
import requests
import time
import asyncio
from datetime import datetime
sys.path.append("/src/bot/cogs/lucknell/")
import utils
from Fermi import Fermi


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class GameShow:
        def __init__(self, member, score=0, quitting=False):
            self.member = member
            self.score = score
            self.quitting = quitting

    @commands.command(aliases=['jouer'])
    async def game(self, ctx, *, game=""):
        client = self.bot
        msg = ctx.message
        if not game:
            await ctx.send("What do you want to do " + (ctx.author.nick if ctx.author.nick != None else ctx.author.name) + "?")
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("https://tenor.com/view/game-over-insert-coins-gif-12235828")
        if msg.content.lower() == "i wish to cross the bridge of death" or game.lower() == "i wish to cross the bridge of death":
            await self.bridge_of_death(ctx)
        elif msg.content.lower() == "mad minute" or game.lower() == "mad minute":
            await self.mad_minute(ctx)
        elif msg.content.lower() == "game show" or game.lower() == "game show":
            await self.game_show(ctx)
        elif msg.content.lower() == "tic tac toe" or msg.content.lower() == "tic-tac-toe" or game.lower() == "tic tac toe" or game.lower() == "tic-tac-toe":
            await self.tic_tac_toe(ctx)
        elif msg.content.lower() == "fermi" or game.lower() == "fermi":
            await self.fermi(ctx)
        else:
            return await ctx.send("You what? Get some $help")

    async def tic_tac_toe(self, ctx):
        client = self.bot
        await ctx.send("This is an beta test")
        await ctx.send("Who do you want to play against?")
        difficulty = None
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Allow me to play the game I select myself")
            msg = None
        if msg:
            member = msg.content.split(" ")[0]
            try:
                player = await msg.guild.fetch_member(int(member.replace("<", "").replace(">", "").replace("@", "").replace("!", "")))
                if player.id != client.user.id:
                    difficulty = "player"
            except discord.errors.NotFound:
                await ctx.send("player not found. Fine I will do it myself")
                player = client.user
            except discord.errors.HTTPException:
                await ctx.send("player not found. Fine I will do it myself")
                player = client.user
            except ValueError:
                await ctx.send("player not found. Fine I will do it myself")
                player = client.user
        if not difficulty:
            await ctx.send("What difficulty?\nEasy\nHard")
            difficulty = "easy"
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("You had one job.")
                return await ctx.send("https://tenor.com/view/south-park-fractured-difficulty-gif-10182175")
            if msg.content.lower() == "hard" or msg.content.lower() == "h":
                difficulty = "hard"
        message = await ctx.send("Loading...")
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await message.add_reaction("3️⃣")
        await message.add_reaction("4️⃣")
        await message.add_reaction("5️⃣")
        await message.add_reaction("6️⃣")
        await message.add_reaction("7️⃣")
        await message.add_reaction("8️⃣")
        await message.add_reaction("9️⃣")
        board = "1️⃣2️⃣3️⃣\n4️⃣5️⃣6️⃣\n7️⃣8️⃣9️⃣"
        vboard = ["c", "c", "c", "c", "c", "c", "c", "c", "c"]
        current = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
                   '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        await message.edit(content=board)
        ticker = await ctx.send(ctx.author.mention + "'s move")

        def check_reaction(user):
            def inner_check(reaction, author):
                return user == author and str(reaction.emoji) in current
            return inner_check

        def check_winner(member):
            if vboard[0] != "c" and vboard[0] == vboard[1] and vboard[1] == vboard[2]:
                return member.mention + " Wins!"
            elif vboard[3] != "c" and vboard[3] == vboard[4] and vboard[4] == vboard[5]:
                return member.mention + " Wins!"
            elif vboard[6] != "c" and vboard[6] == vboard[7] and vboard[7] == vboard[8]:
                return member.mention + " Wins!"
            elif vboard[0] != "c" and vboard[0] == vboard[3] and vboard[3] == vboard[6]:
                return member.mention + " Wins!"
            elif vboard[1] != "c" and vboard[1] == vboard[4] and vboard[4] == vboard[7]:
                return member.mention + " Wins!"
            elif vboard[2] != "c" and vboard[2] == vboard[5] and vboard[5] == vboard[8]:
                return member.mention + " Wins!"
            elif vboard[0] != "c" and vboard[0] == vboard[4] and vboard[4] == vboard[8]:
                return member.mention + " Wins!"
            elif vboard[2] != "c" and vboard[2] == vboard[4] and vboard[4] == vboard[6]:
                return member.mention + " Wins!"
            else:
                return None

        def check_bot_win():
            if vboard[0] != "c" and vboard[0] == vboard[1] and vboard[1] == vboard[2]:
                return "I win!"
            elif vboard[3] != "c" and vboard[3] == vboard[4] and vboard[4] == vboard[5]:
                return "I win!"
            elif vboard[6] != "c" and vboard[6] == vboard[7] and vboard[7] == vboard[8]:
                return "I win!"
            elif vboard[0] != "c" and vboard[0] == vboard[3] and vboard[3] == vboard[6]:
                return "I win!"
            elif vboard[1] != "c" and vboard[1] == vboard[4] and vboard[4] == vboard[7]:
                return "I win!"
            elif vboard[2] != "c" and vboard[2] == vboard[5] and vboard[5] == vboard[8]:
                return "I win!"
            elif vboard[0] != "c" and vboard[0] == vboard[4] and vboard[4] == vboard[8]:
                return "I win!"
            elif vboard[2] != "c" and vboard[2] == vboard[4] and vboard[4] == vboard[6]:
                return "I win!"
            else:
                return None

        while len(current) != 0:
            await ticker.edit(content=ctx.author.mention + "'s move")
            try:
                # returns a tuple with a reaction and member object
                reaction, member = await client.wait_for('reaction_add', timeout=30, check=check_reaction(ctx.author))
            except asyncio.TimeoutError:
                return await ticker.edit(content="The game timed out")
            await ticker.edit(content="Nice choice!")
            if not str(reaction.emoji) in current:
                return await ctx.send("wait that was illegal")
            current.remove(reaction.emoji)
            board = board.replace(reaction.emoji, "❌")
            num = int(reaction.emoji[0])
            vboard[num - 1] = "x"
            await message.edit(content=board)
            win = check_winner(member)
            if win:
                return await ticker.edit(content=win)
            if len(current) == 0:
                return await ticker.edit(content="This game is over")
            if difficulty == "player":
                await ticker.edit(content=player.mention + "'s move")
            else:
                await ticker.edit(content="My move")
            if difficulty == "hard":
                if vboard[4] == "c":
                    choice = current.index("5️⃣")
                elif vboard[0] == "x" and vboard[0] == vboard[1] and vboard[2] == "c":
                    choice = current.index("3️⃣")
                elif vboard[1] == "x" and vboard[1] == vboard[2] and vboard[0] == "c":
                    choice = current.index("1️⃣")
                elif vboard[2] == "x" and vboard[2] == vboard[0] and vboard[1] == "c":
                    choice = current.index("2️⃣")
                elif vboard[3] == "x" and vboard[3] == vboard[4] and vboard[5] == "c":
                    choice = current.index("6️⃣")
                elif vboard[4] == "x" and vboard[4] == vboard[5] and vboard[3] == "c":
                    choice = current.index("4️⃣")
                elif vboard[5] == "x" and vboard[5] == vboard[3] and vboard[4] == "c":
                    choice = current.index("5️⃣")
                elif vboard[6] == "x" and vboard[6] == vboard[7] and vboard[8] == "c":
                    choice = current.index("9️⃣")
                elif vboard[7] == "x" and vboard[7] == vboard[8] and vboard[6] == "c":
                    choice = current.index("7️⃣")
                elif vboard[8] == "x" and vboard[8] == vboard[6] and vboard[7] == "c":
                    choice = current.index("8️⃣")
                elif vboard[0] == "x" and vboard[0] == vboard[6] and vboard[3] == "c":
                    choice = current.index("4️⃣")
                elif vboard[0] == "x" and vboard[0] == vboard[3] and vboard[6] == "c":
                    choice = current.index("7️⃣")
                elif vboard[3] == "x" and vboard[3] == vboard[6] and vboard[0] == "c":
                    choice = current.index("1️⃣")
                elif vboard[1] == "x" and vboard[1] == vboard[7] and vboard[4] == "c":
                    choice = current.index("5️⃣")
                elif vboard[1] == "x" and vboard[1] == vboard[4] and vboard[7] == "c":
                    choice = current.index("8️⃣")
                elif vboard[4] == "x" and vboard[4] == vboard[7] and vboard[1] == "c":
                    choice = current.index("2️⃣")
                elif vboard[2] == "x" and vboard[2] == vboard[8] and vboard[5] == "c":
                    choice = current.index("6️⃣")
                elif vboard[2] == "x" and vboard[2] == vboard[5] and vboard[8] == "c":
                    choice = current.index("9️⃣")
                elif vboard[5] == "x" and vboard[5] == vboard[8] and vboard[2] == "c":
                    choice = current.index("3️⃣")
                elif vboard[4] == "x" and vboard[4] == vboard[0] and vboard[8] == "c":
                    choice = current.index("9️⃣")
                elif vboard[4] == "x" and vboard[4] == vboard[2] and vboard[6] == "c":
                    choice = current.index("7️⃣")
                elif vboard[4] == "x" and vboard[4] == vboard[8] and vboard[0] == "c":
                    choice = current.index("1️⃣")
                elif vboard[4] == "x" and vboard[4] == vboard[6] and vboard[2] == "c":
                    choice = current.index("3️⃣")
                else:
                    choice = random.randint(0, len(current) - 1)
            elif difficulty == "easy":
                choice = random.randint(0, len(current) - 1)
            if difficulty != "player":
                board = board.replace(current[choice], "⭕")
                num = int(current[choice][0])
                vboard[num - 1] = "o"
                current.remove(current[choice])
                win = check_bot_win()
            else:
                try:
                    reaction, member = await client.wait_for('reaction_add', timeout=30, check=check_reaction(player))
                except asyncio.TimeoutError:
                    return await ticker.edit(content="The game timed out")
                await ticker.edit(content="Nice choice!")
                if not str(reaction.emoji) in current:
                    return await ctx.send("wait that was illegal")
                current.remove(reaction.emoji)
                board = board.replace(reaction.emoji, "⭕")
                num = int(reaction.emoji[0])
                vboard[num - 1] = "o"
                win = check_winner(player)
            await message.edit(content=board)
            if win:
                return await ticker.edit(content=win)

    async def fermi(self, ctx):
        client = self.bot
        rounds = 5
        await ctx.send((ctx.author.nick if ctx.author.nick != None else ctx.author.name) + " Normal(3 digits) or hard(5 digits)?")
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Seems like you want 3")
            size = 3
        if msg and (msg.content.lower() == "hard" or msg.content.lower() == "h" or msg.content.lower() == "5"):
            size = 5
        else:
            size = 3
        winning = "Fermi " * size
        f = Fermi(size)
        await ctx.send((ctx.author.nick if ctx.author.nick != None else ctx.author.name) + " at anytime you can type quit to quit\nWhat is your first guess?")
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Nothing? Got it.")
        win = f.check_win(msg.content)
        await ctx.send(win)
        rounds -= 1
        while (rounds > 0 and win != winning) and msg.content.lower() != "quit":
            await ctx.send((ctx.author.nick if ctx.author.nick != None else ctx.author.name) + "\nWhat is your next guess? (Guesses remaining {})".format(rounds))
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("Nothing? Got it. The answer was {}".format(f.get_cheats()))
            win = f.check_win(msg.content)
            await ctx.send(win)
            rounds -= 1
        if msg.content.lower() == "quit":
            return await ctx.send("~~You did your best~~ You gave up. The answer was {}".format(f.get_cheats()))
        if win == winning:
            return await ctx.send("You got it!")
        else:
            return await ctx.send("There is always next time. The answer was {}".format(f.get_cheats()))

    async def game_show(self, ctx, replay=None):
        client = self.bot
        if not replay:
            rounds = 3
            difficulties = ["easy", "median", "hard"]
            await ctx.send("So who is playing?")
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("No one? Got it.")
            players = msg.content.split(" ")
            confirmed_players = []
            confirmed_players.append(self.GameShow(ctx.author))
            for player in players:
                try:
                    member = await msg.guild.fetch_member(int(player.replace("<", "").replace(">", "").replace("@", "").replace("!", "")))
                except discord.errors.NotFound:
                    continue
                except discord.errors.HTTPException:
                    continue
                except ValueError:
                    continue
                # for cplayer in confirmed_players:
                #    if member == cplayer.member:
                #       yield cplayer
                result = [
                    cplayer for cplayer in confirmed_players if member == cplayer.member]
                if result:
                    continue
                await ctx.send("Do you wish to play {} ?".format(member.mention))
                try:
                    msg = await client.wait_for('message', check=utils.check(member), timeout=60)
                except asyncio.TimeoutError:
                    await ctx.send("No response? Fine then.")
                    continue
                if msg.content.lower() == "yes":
                    await ctx.send("Welcome aboard")
                    confirmed_players.append(self.GameShow(member))
                else:
                    await ctx.send("Someone is chicken")
            await ctx.send("What difficulty do you want to pick?\nEasy\nMedium\nHard\nAuto\nRandom")
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("No response? Then we will do random")
                msg = None
            if msg:
                if msg.content.lower() in difficulties:
                    difficulty = msg.content.lower()
                elif msg.content.lower() == "auto":
                    await ctx.send("auto is not supported yet. Good luck on random difficulty")
                    difficulty = ""
                else:
                    difficulty = ""
            else:
                difficulty = ""
            await ctx.send("How many rounds?")
            try:
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("No response? Then we will do " + str(rounds) + " rounds")
            if utils.is_int(msg.content):
                rounds = int(msg.content)
                if (rounds * len(confirmed_players)) > 50:
                    await ctx.send("Too many rounds given a max of 50 questions will be given.")
                    rounds = 50 // len(confirmed_players)
        else:
            rounds = replay[0]
            difficulty = replay[1]
            confirmed_players = replay[2]
        await ctx.send("That appears to be everyone but lets list them here")
        names = ""
        for player in confirmed_players:
            names += player.member.mention
            names += "\n"
        await ctx.send(names + "\nMay the odds be ever in your favor\nto quit say the following\n**I wish to quit**")
        q_number = rounds * len(confirmed_players)
        url = "https://opentdb.com/api.php?amount=" + \
            str(q_number) + "&difficulty=" + difficulty
        try:
            api_QA = requests.get(url).json()
        except requests.exceptions.RequestException as e:
            return await ctx.send("I have a bug. Tell my creator\n", e)
        j = 0
        quitting = False
        while j < q_number and not quitting:
            for player in confirmed_players:
                question = ""
                if player.quitting:
                    j += 1
                    continue
                try:
                    if api_QA["results"][j]["type"] == "boolean":
                        question += "True or False?\n"
                    question += utils.decodeHTMLSymbols(
                        api_QA["results"][j]["question"])
                    if api_QA["results"][j]["type"] == "multiple":
                        choices = []
                        choices.append(utils.decodeHTMLSymbols(
                            api_QA["results"][j]["correct_answer"]))
                        for ans in api_QA["results"][j]["incorrect_answers"]:
                            choices.append(utils.decodeHTMLSymbols(ans))
                        question += "\nChoices:\n"
                        while len(choices) > 1:
                            i = random.randint(0, len(choices) - 1)
                            question += (choices[i] + "\n")
                            del choices[i]
                        question += choices[0]
                    answer = utils.decodeHTMLSymbols(
                        api_QA["results"][j]["correct_answer"])
                    j += 1
                except KeyError as e:
                    return await ctx.send("I have a bug in my API usage. Please open an issue with my creator and tell him\n", e)
                await ctx.send(player.member.mention + "\n" + question)
                try:
                    msg = await client.wait_for('message', check=utils.check(player.member), timeout=30)
                except asyncio.TimeoutError:
                    msg = "No reply"
                if msg == "No reply":
                    await ctx.send("The correct answer was " + answer)
                elif msg.content.lower() == answer.lower():
                    await msg.add_reaction('✅')
                    await ctx.send("correct!")
                    player.score += 1
                elif msg.content.lower() == "i wish to quit":
                    await ctx.send("Do you wish to quit " + (player.member.nick if player.member.nick != None else player.member.name) + "?")
                    try:
                        msg = await client.wait_for('message', check=utils.check(player.member), timeout=30)
                    except asyncio.TimeoutError:
                        pass
                    if msg.content.lower() == "yes":
                        player.quitting = True
                        await ctx.send("Alright quitter")
                else:
                    await msg.add_reaction('❎')
                    await ctx.send("Wrong. The correct answer was " + answer)
                if quitting:
                    break
                await asyncio.sleep(2)
        await ctx.send("Thanks for playing here are the final results")
        final_results = ""
        for player in confirmed_players:
            if player.quitting:
                final_results += "~~" + \
                    (player.member.nick if player.member.nick != None else player.member.name) + "'s~~ Quitter Score: " + \
                    str(player.score) + "\n"
            else:
                final_results += (player.member.nick if player.member.nick != None else player.member.name) + \
                    "'s Score: " + str(player.score) + "\n"
        await ctx.send(final_results)
        await ctx.send("Wanna play again?")
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("No? Got it.")

        if msg.content.lower() == "yes" or msg.content.lower() == "y":
            for player in confirmed_players:
                player.score = 0
            await self.game_show(ctx, (rounds, difficulty, confirmed_players))

    async def bridge_of_death(self, ctx):
        client = self.bot
        colors = ["red", "green", "blue", "black", "white",
                  "yellow", "orange", "brown", "pink", "purple", "gray", "grey"]
        await ctx.send("He who wishes to cross the bridge of Death, must answer me these questions three")
        await asyncio.sleep(2)
        await ctx.send('What is your name?')
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            return await self.failure(ctx)
        if not msg.content.lower() == ctx.author.name.lower() and not msg.content.lower() == ctx.author.nick.lower():
            return await self.failure(ctx)
        name = msg.content
        await ctx.send(name + '\nWhat is your favorite color?')
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            await self.failure(ctx)
            return
        if not msg.content.lower() in colors:
            await self.failure(ctx)
            return
        q3 = random.randint(1, 10)
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        if q3 == 1:
            question = "What is {}+{}?".format(x, y)
            answer = str(x+y)
        elif q3 == 2:
            question = "What is {}-{}?".format(x, y)
            answer = str(x-y)
        elif q3 == 3:
            question = "What year is it?"
            answer = str(datetime.now().year)
        elif q3 == 4:
            question = "What is the airspeed velocity of an unladen swallow?"
            answer = "african or european?"
        elif q3 > 4:
            url = "https://opentdb.com/api.php?amount=1"
            try:
                api_QA = requests.get(url).json()
            except requests.exceptions.RequestException as e:
                return await ctx.send("I have a bug. Tell my creator\n" + e)
            question = ""
            try:
                if api_QA["results"][0]["type"] == "boolean":
                    question += "True or False?\n"
                question += utils.decodeHTMLSymbols(
                    api_QA["results"][0]["question"])
                if api_QA["results"][0]["type"] == "multiple":
                    choices = []
                    choices.append(utils.decodeHTMLSymbols(
                        api_QA["results"][0]["correct_answer"]))
                    for ans in api_QA["results"][0]["incorrect_answers"]:
                        choices.append(utils.decodeHTMLSymbols(ans))
                    question += "\nChoices:\n"
                    while len(choices) > 1:
                        i = random.randint(0, len(choices) - 1)
                        question += (choices[i] + "\n")
                        del choices[i]
                    question += choices[0]
                answer = utils.decodeHTMLSymbols(
                    api_QA["results"][0]["correct_answer"])
            except KeyError as e:
                return await ctx.send("I have a bug in my API usage. Please open an issue with my creator and tell him\n" + e)
        else:
            return await ctx.send("You really should not be seeing this...")
        await ctx.send(name + "\n" + question)
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=15)
        except asyncio.TimeoutError:
            return await self.failure(ctx)
        if q3 == 4 and str(msg.content).lower() == answer.lower():
            await ctx.send("Huh? I… I don’t know that.")
            return await ctx.send("https://i.makeagif.com/media/8-06-2015/6tzcHH.gif")
        if not str(msg.content).lower() == answer.lower():
            return await self.failure(ctx)
        await ctx.send("Be on your way")
        return await ctx.send("https://tenor.com/view/monty-python-holy-grail-horse-gif-3448553")

    # A math game that tormented me when I was younger because multiplication was hard

    async def mad_minute(self, ctx):
        client = self.bot
        await ctx.send("You will have 1 minute to answer some multiplication problems. Good luck!")
        await asyncio.sleep(2)
        attempts = 0
        correct = 0
        await ctx.send("Go!")
        start = time.time()
        while time.time() - start <= 60:
            x = random.randint(0, 12)
            y = random.randint(0, 12)
            await ctx.send("What is {}x{}?".format(x, y))
            try:
                limit = 60 - (time.time() - start)
                msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=limit)
                if (msg.content == str(x*y)):
                    correct += 1
                attempts += 1
            except asyncio.TimeoutError:
                pass
        if attempts != 0:
            await ctx.send("You made {} attempt(s) and got {} correct".format(attempts, correct))
        else:
            await ctx.send("You did nothing.")

    async def failure(self, ctx):
        fails = ["https://tenor.com/view/monty-python-bridge-yellow-gif-9412030",
                 "https://thumbs.gfycat.com/AlarmingBestBooby-mobile.mp4"]
        await ctx.send(fails[random.randint(0, len(fails) - 1)])


def setup(bot):
    bot.add_cog(Game(bot))
