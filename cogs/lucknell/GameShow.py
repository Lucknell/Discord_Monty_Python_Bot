import random
import requests
import asyncio
import discord
from discord.ext import commands
from . import utils

class GameShow:
    class Question:
        def __init__(self, question, answers, correct_answer, qtype):
            self.question = question
            self.answers = answers
            self.correct_answer = correct_answer
            self.type = qtype
            
    class Player:
        def __init__(self, member, score=0, quitting=False):
            self.member = member
            self.score = score
            self.quitting = quitting
    
    class OpenTDB:
        def __init__(self):
            self.categories = {"Any": "any",
                    "General Knowledge":"&category=9",
                    "Entertainment: Book": "&category=10",
                    "Entertainment: Film": "&category=11",
                    "Entertainment: Music": "&category=12",
                    "Entertainment: Musicals & Theatres": "&category=13",
                    "Entertainment: Television": "&category=14",
                    "Entertainment: Video Games": "&category=15",
                    "Entertainment: Board Games": "&category=16",
                    "Science & Nature": "&category=17",
                    "Science: Computers": "&category=18",
                    "Science: Mathematics": "&category=19",
                    "Mythology": "&category=20",
                    "Sports": "&category=21",
                    "Geography": "&category=22",
                    "History": "&category=23",
                    "Politics": "&category=24",
                    "Art": "&category=25",
                    "Celebrities": "&category=26",
                    "Animals": "&category=27",
                    "Vehicles": "&category=28",
                    "Entertainment: Comics": "&category=29",
                    "Science Gadgets": "&category=30",
                    "Entertainment: Anime & Manga": "&category=31",
                    "Entertainment: Cartoons & Animations": "&category=32"}
            self.api = "https://opentdb.com/api.php?"
            self.difficulty_options = ["easy", "medium", "hard", "random"]


    class TheTrivia:
        def __init__(self):
            self.categories = {"Any": "any",
                "Music": "music",
                "Sports and Leisure":"sport_and_leisure",
                "Film and TV":"film_and_tv",
                "Arts and Literature":"arts_and_literature",
                "History":"history",
                "Society and Culture":"society_and_culture",
                "Science":"science",
                "Geography":"geography",
                "Food and Drink":"food_and_drink",
                "General Knowledge":"general_knowledge"}
            self.api = "https://the-trivia-api.com/v2/questions/?"
            self.difficulty_options = ["easy", "medium", "hard", "random"]
     
    
    class BetaTrivia:
        def __init__(self):
            self.categories = {"Any": "any",
                "Entertainment": "Entertainment",
                "Sports": "Sports",
                "Science":"Science",
                "Animals": "Animals",
                "General Knowledge":"General Knowledge",
                "Mythology": "Mythology",
                "Politics": "Politics",
                "Geography": "Geography",
                "History":"History"}
            self.api = "https://beta-trivia.bongobot.io/?"
            self.difficulty_options = ["easy", "medium", "hard"]
    
       
    def __init__(self):
        self.players = []
        self.questions = []
        self.quest_num = None
        self.difficulty = None
        self.category = None
        self.api_url = None
        self.game = None
        

    async def build_api_url(self, quest_num, difficulty, category, game):
        self.quest_num = quest_num
        self.difficulty = difficulty
        self.category = category
        self.api_url = game.api
        self.game = game
        if isinstance(game, self.OpenTDB):
            self.api_url = f"{self.api_url}amount={quest_num}&difficulty={difficulty}{category}"
        elif isinstance(game, self.TheTrivia):
            self.api_url = f"{self.api_url}limit={quest_num}"
            if difficulty != "":
                self.api_url =f"{self.api_url}&difficulties={difficulty}"
            if category != "":
                self.api_url = f"{self.api_url}&categories={category}"
        elif isinstance(game, self.BetaTrivia):
            self.api_url = f"{self.api_url}/?search=cat&difficulty={difficulty}"
            __limit = quest_num
            if category != "":
                self.api_url = f"{self.api_url}&category={category}"
            if __limit > 10:
                __limit = 10
            self.api_url = f"{self.api_url}&limit={__limit}"

        else:
            print("Invalid game object passed. raise an exception")

    async def get_questions(self, ctx, game):
        try:
            api_QA = requests.get(self.api_url).json()
        except requests.exceptions.RequestException as e:
            return await ctx.send("I have a bug. Tell my creator\n", e)
        self.questions = []
        if isinstance(game, self.OpenTDB):
            for QA in api_QA["results"]:
                self.questions.append(self.Question(QA["question"], QA["incorrect_answers"], QA["correct_answer"], QA["type"]))
        elif isinstance(game, self.TheTrivia):
            for QA in api_QA:
                self.questions.append(self.Question(QA["question"]["text"], QA["incorrectAnswers"], QA["correctAnswer"], QA["type"]))
        elif isinstance(game, self.BetaTrivia):
            #we need to call the api more times
            iterations = int(self.quest_num/10)
            remainder = self.quest_num%10
            for i in range(iterations):
                api_QA = requests.get(self.api_url).json()
                for QA in api_QA:
                    self.questions.append(self.Question(QA["question"], QA["incorrect_answers"], QA["correct_answer"], QA["type"]))
            self.build_api_url(remainder, self.difficulty, self.category, self.game)
            api_QA = requests.get(self.api_url).json()
            for QA in api_QA:
                self.questions.append(self.Question(QA["question"], QA["incorrect_answers"], QA["correct_answer"], QA["type"]))
            

    async def setup_game(self, ctx, thread, client):
        apis = ["Opentdb", "The Trivia API", "Beta Trivia"]
        list_of_options = []
        view = discord.ui.View()
        for label in apis:
            list_of_options.append(discord.SelectOption(label = label, value = label))
        view.add_item(item=discord.ui.Select(options=list_of_options, custom_id="Category"))
        await thread.send("Which service?", view=view)
        try:
            msg = await client.wait_for('interaction', check=utils.check_select_interaction(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            await thread.send("OpenTDB selected.")
            game = self.OpenTDB()
            msg = None
        category = None
        for item in view.children:
            index = view.children.index(item)
            view.children[index].disabled = True
            if msg and "Category" == msg.data["custom_id"]:
                api_name = item.values[0]
                item.placeholder = api_name
                game = None
                if api_name.lower() == "the trivia api":
                    game = self.TheTrivia()
                elif api_name.lower() ==  "beta trivia":
                    game = self.BetaTrivia()
                else:
                    game = self.OpenTDB()
        await msg.response.edit_message(view=view)
        rounds = 3
        view = discord.ui.View()
        users = discord.ui.UserSelect(custom_id ="users", placeholder = "Choose your opponents! Max 25", max_values = 25)
        view.add_item(item=users)
        if len(self.players) == 0:
            self.players = []
            self.players.append(self.Player(ctx.author))
            btn = discord.ui.Button(style = discord.ButtonStyle.blurple,label="Just me")
            view.add_item(item=btn)
            await thread.send("So who is playing?", view=view)
        else:
            btn = discord.ui.Button(style = discord.ButtonStyle.blurple,label="No one")
            view.add_item(item=btn)
            await thread.send("Any new players?",view=view)
        msg = None
        try:
            msg = await client.wait_for('interaction', check=utils.check_interaction_from_user(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            return await thread.send("No one? Got it.")
        players = []
        for item in view.children:
            view.children[index].disabled = True
            if item.custom_id == msg.data["custom_id"] and item.custom_id == "users":
                players = item.values
        await msg.response.edit_message(view=view)
        for player in players:
            if player.bot:
                continue
            result = [
                cplayer for cplayer in self.players if player == cplayer.member]
            if result:
                continue
            view = discord.ui.View()
            btn = discord.ui.Button(style = discord.ButtonStyle.green,
                    custom_id="yes",
                    label="Yes")
            view.add_item(item = btn)
            btn = discord.ui.Button(style = discord.ButtonStyle.danger,
                    custom_id="no",
                    label="No")
            view.add_item(item = btn)
            await thread.send(f"Do you wish to play {player.mention}", view=view)
            try:
                msg = await client.wait_for('interaction', check=utils.check_interaction(player), timeout=60)
            except asyncio.TimeoutError:
                await thread.send("No response? Fine then.")
                continue
            for item in view.children:
                index = view.children.index(item)
                view.children[index].disabled = True
                if item.custom_id == msg.data["custom_id"]:
                    yes_no = item.label
            await msg.response.edit_message(view=view)
            if yes_no.lower() == "yes":
                await thread.send("Welcome aboard")
                self.players.append(self.Player(player))
            else:
                await thread.send("Someone is chicken")
        bid = 1
        view = discord.ui.View()
        for diff in game.difficulty_options:
            btn = discord.ui.Button(style = discord.ButtonStyle.blurple,
                    custom_id="button" + str(bid),
                    label=diff)
            bid += 1
            view.add_item(item = btn)
        await thread.send("What difficulty do you want to pick?", view=view)
        try:
            msg = await client.wait_for('interaction', check=utils.check_interaction(ctx.author), timeout=30)
        except asyncio.TimeoutError:
            await thread.send("Hard selected.")
            msg = None
        for item in view.children:
            index = view.children.index(item)
            view.children[index].disabled = True
            if item.custom_id == msg.data["custom_id"]:
                difficulty = item.label
        await msg.response.edit_message(view=view)
        if msg is None:
            difficulty = "hard"
        if difficulty == "random":
            difficulty = ""
        list_of_options = []
        view = discord.ui.View()
        for label, value in game.categories.items():
            list_of_options.append(discord.SelectOption(label = label, value = value))
        view.add_item(item=discord.ui.Select(options = list_of_options, custom_id = "Category"))
        await thread.send("What Category?", view=view)
        try:
            msg = await client.wait_for('interaction', check=utils.check_select_interaction(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            await thread.send("Any selected.")
            msg = None
        category = None
        for item in view.children:
            index = view.children.index(item)
            view.children[index].disabled = True
            if item.custom_id == msg.data["custom_id"]:
                category = item.values[0]
                list_of_keys = list(game.categories.keys())
                list_of_values = list(game.categories.values())
                item.placeholder = list_of_keys[list_of_values.index(item.values[0])]
        await msg.response.edit_message(view=view)
        await thread.send("How many rounds?")
        try:
            msg = await client.wait_for('message', check=utils.check(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            await thread.send("No response? Then we will do " + str(rounds) + " rounds")
        if utils.is_int(msg.content):
            rounds = int(msg.content)
            if (rounds * len(self.players)) > 50:
                await thread.send("Too many rounds given a max of 50 questions will be given.")
                rounds = 50 // len(self.players)
        await thread.send("That appears to be everyone but lets list them here")
        names = ""
        for player in self.players:
            names += player.member.mention
            names += "\n"
        await thread.send(names + "\nMay the odds be ever in your favor\nto quit **Click Quit**")
        quest_num = rounds * len(self.players)
        if category == "any":
            category = ""
        await self.build_api_url(quest_num, difficulty, category, game)


    async def run_game(self, ctx, thread, client):
        await self.get_questions(ctx, self.game)
        j = -1
        ans_choices = ["A","B","C","D"]
        while j < self.quest_num:
            for player in self.players:
                j +=1
                mult_choice = {}
                if j == self.quest_num:
                    break
                if player.quitting:
                    continue
                current_q = self.questions[j]
                prompt = ""
                choices = []
                if current_q.type == "boolean":
                    prompt += f"True or False?\n"
                if current_q.type == "multiple" or current_q.type == "text_choice":
                    index = 0
                    choices.append(utils.decodeHTMLSymbols(current_q.correct_answer))
                    for ans in current_q.answers:
                        choices.append(utils.decodeHTMLSymbols(ans))
                prompt += f"{utils.decodeHTMLSymbols(current_q.question)}\nChoices:\n"
                while len(choices) > 0:
                    i = random.randint(0, len(choices) - 1)
                    prompt += f"{ans_choices[index]}) {choices[i]}\n"
                    mult_choice[ans_choices[index]] = choices[i]
                    index += 1
                    del choices[i]
                view = discord.ui.View()
                bid = 1
                if current_q.type == "multiple" or current_q.type == "text_choice":
                    for ans in ans_choices:
                        btn = discord.ui.Button(style = discord.ButtonStyle.gray,
                                custom_id="button" + str(bid),
                                label=ans)
                        bid += 1
                        view.add_item(item=btn)
                else:
                    bool_choices = ["True", "False"]
                    for ans in bool_choices:
                        btn = discord.ui.Button(style = discord.ButtonStyle.green,
                                custom_id="button" + str(bid),
                                label=ans)
                        bid += 1
                        view.add_item(item = btn)
                btn = discord.ui.Button(style = discord.ButtonStyle.danger,
                                custom_id="buttonq",
                                label="Quit")
                view.add_item(item = btn)
                await thread.send(f"{player.member.mention}\n{prompt}", view=view)
                try:
                    msg = await client.wait_for('interaction', check=utils.check_interaction(player.member), timeout=30)
                except asyncio.TimeoutError:
                    await thread.send(f"The correct answer was {utils.decodeHTMLSymbols(current_q.correct_answer)}")
                    msg = None
                for item in view.children:
                    index = view.children.index(item)
                    view.children[index].disabled = True
                    if msg and item.custom_id == msg.data["custom_id"]:
                        if item.label.lower() == "quit":
                            user_answer = item.label
                        elif current_q.type == "multiple" or current_q.type == "text_choice":
                            user_answer = mult_choice[item.label]
                        else:
                            user_answer = item.label
                if msg is None:
                    continue
                await msg.response.edit_message(view=view)
                if user_answer.lower() == utils.decodeHTMLSymbols(current_q.correct_answer.lower()):
                    msg = await thread.send(utils.decodeHTMLSymbols(current_q.correct_answer) + "\ncorrect!")
                    await msg.add_reaction('✅')
                    player.score += 1
                elif user_answer.lower() == "quit":
                    player.quitting = True
                    await thread.send(f"Alright quitter the answer was {utils.decodeHTMLSymbols(current_q.correct_answer)}")
                else:
                    msg = await thread.send(f"{user_answer}?\nWrong. The correct answer was {utils.decodeHTMLSymbols(current_q.correct_answer)}.")
                    await msg.add_reaction('❎')
                await asyncio.sleep(2)
        await thread.send("Thanks for playing here are the final results")
        final_results = ""
        for player in self.players:
            if player.quitting:
                final_results += f"~~{player.member.display_name}'s~~ Quitter Score: {player.score}\n"
            else:
                final_results += f"{player.member.display_name}'s Score: {player.score}\n"
        await thread.send(final_results)
        view = discord.ui.View()
        btn = discord.ui.Button(style = discord.ButtonStyle.green,
                custom_id="yes",
                label="Yes")
        view.add_item(item = btn)
        btn = discord.ui.Button(style = discord.ButtonStyle.danger,
                custom_id="no",
                label="No")
        view.add_item(item = btn)
        btn = discord.ui.Button(style = discord.ButtonStyle.blurple,
                custom_id="change_settings",
                label="Change Settings")
        view.add_item(item = btn)
        await thread.send("Wanna play again?", view=view)
        try:
            msg = await client.wait_for('interaction', check=utils.check_interaction(ctx.author), timeout=60)
        except asyncio.TimeoutError:
            return await thread.send("No? Got it.")
        for item in view.children:
            index = view.children.index(item)
            view.children[index].disabled = True
            if item.custom_id == msg.data["custom_id"]:
                yes_no = item.label
        await msg.response.edit_message(view=view)
        if yes_no.lower() == "yes":
            for player in self.players:
                player.score = 0
            await self.run_game(ctx, thread,client)
        elif yes_no.lower() == "change settings":
            for player in self.players:
                player.score = 0
            await self.setup_game(ctx, thread, client)
            await self.run_game(ctx, thread, client)