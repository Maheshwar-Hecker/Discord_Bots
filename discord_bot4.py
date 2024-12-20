import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os, random, re, asyncio
from datetime import datetime, timezone
from blackAPI import BlackBox

discord_bots = ["Punnet Superstar", "Titu Mama"]
discord_bots_generalNames = {
    "Punnet Superstar": ["punnetSuperstar", "Punnet Bhai"],
    "Titu Mama": ["tituMama", "Mama"]
}


# extracts message for special cases
def extract_message(line):
    # Match number and period, optional spaces, and then the quoted message
    line = re.sub(r'"', '', line, flags=re.IGNORECASE)
    match = re.match(r'^\d+\.\s?"(.+)"$', line)
    if match:
        return match.group(1)  # If the message is in quotes, return the message
    else:
        # Handle case where there's no quote, just a message after the number
        match = re.match(r'^\d+\.\s?(.+)$', line)
        if match:
            return match.group(1).strip()  # Return the message without quotes and number

    # If no match found, return the original line
    return line.strip()


def giveIntro(Bot_name: str):
    """Returns  intro in the typical style of the bot personality"""
    intro = ""
    try:
        with open(os.path.join(f"{Bot_name}_Personality", f"introduction_{Bot_name}.txt"), "r+") as file:
            lines = file.readlines()
            for line in lines:
                if line.strip():  # Ignore blank lines
                    intro += line.strip() + " #$0$# "  # Add separator
    except Exception as e:
        print(f"File opening error:{e}")
    if intro == "":  # sometimes it was getting an empty string
        intro = giveIntro(Bot_name)
    # Now intro is done
    return random.choice(intro.split("#$0$#")).replace("{", "").replace("}", "").replace(";", "")


# This is a class which handles behaviour and attributes of BOT and switching between the bot personality is easy and
# can be done by changing the bot name only because everything is synced with bot name
class bot_behaviour(commands.Bot):
    def __init__(self, bot_name, bot_general_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initialising the bot
        self.bot_name = bot_name
        self.bot_refer_name = bot_general_name
        self.bot_name_personality = f"{self.bot_name}_Personality"
        self.guilds_bot_isPart = []
        self.channelIDs = []
        self.interacting_channelID = None

        # bot personality improvement
        self.moods = ["peace", "fun", "sad", "angry", "happy"]
        self.mood = random.randint(1,
                                   5)  # if mood ==1 peace, mood ==2 fun(games/music suggestion) , mood ==3 sad ,mood ==4 angry, mood ==5 happy
        self.bot_mood_changeAutomatic = True

        # user experience improvement
        self.numberOfTimesUserPreferenceIsAsked = []

        # initialise Searching Internet API
        self.internet = BlackBox()

        #bot's memory
        self.memory ={}

        # Register commands when the bot starts
        self.add_slash_commands()

    # defines bot behaviour when it is ready to perform
    async def on_ready(self):  # prints a message when successful login is achieved
        print(f"Logged in as {self.bot_refer_name} in Discord")
        try:
            await self.tree.sync()  # Sync the slash commands with Discord
            print("Slash commands have been synced.")
            # getting the guild ids and channel ids of the bots
            self.guilds_bot_isPart = [guild for guild in self.guilds]
            self.channelIDs = [channel_c.id for guild in self.guilds_bot_isPart for channel_c in guild.channels]
            print(self.guilds_bot_isPart)
            print(self.channelIDs)
            print("Giving intro to all the channels")  # gives intro to all th channels that iam ready
            for id_ in self.channelIDs:
                channel = self.get_channel(id_)
                if channel.type == discord.ChannelType.text:
                    await channel.send(giveIntro(self.bot_name))
            print("SuccessFull")
            print("Getting users for all guilds- -channels")
            self.markDown_users()  # marking users connected with bot on any channel
            print("SuccessFull")
            print("Retrieving Bot's Memory")
            self.memory = self.getMemory()
            print("SuccessFull")

            print("Bot is ready in every aspect")

        except Exception as e:  # to handle any exceptions
            print(f"Unsuccessful due to : {e}")

    def getMemory(self):
        """Memory is stored in a folder memory if no such folder then a message of memory loss...
            memory folder has text files a guild_name#userID.txt
            where each user profile will be saved
            *username->name
            *userId->id
            *userDescription->things about user told the bot
            *favourite songs->songs_data delimited by '[/]' used in later
            where song data is stores like this
            {songName};{userRating in range (1 to 10)};{No. of times played};
        """
        memory={}
        try :
            if os.path.exists("memory") and os.path.isdir("memory"):
                #bot has memory
                print(1)
                for guild in self.guilds_bot_isPart:
                    print(2)
                    for member in guild.members:
                        print(3)
                        userP = {}
                        filepath = os.path.join("memory",f"{guild.name}#{member.id}.txt")
                        if os.path.exists(filepath):
                            print("Uploading memory...")
                            with open(filepath,"r") as memberProfile:
                                memberProfile.seek(0)
                                profile = memberProfile.readlines()
                                for tag in profile:
                                    key, value = tag.strip().split("->")
                                    if value == "N/A":value=""
                                    userP[key] = value
                            memory[f"{member.id}"] = userP
                        else:
                            #case where used joins when bot was not present when bot was intitiated and no memory found
                            print("No MemoryFound for user with id ",member.id)
                            print("Making memory for him")
                            with open(os.path.join("memory", f"{guild.name}#{member.id}.txt"), "w") as memberProfile:
                                memberProfile.write(f"username->{member.name}\n")
                                memberProfile.write(f"userID->{member.id}\n")
                                memberProfile.write(f"information->N/A\n")
                                memberProfile.write(f"favouriteSongs->N/A\n")
                            return self.getMemory()
            else:
                print("No memory or complete memory loss...")
                print("Making memory")
                self.makeMemory()
                return self.getMemory()
        except Exception as e:
            print(f"Some error occurred while getting the file as :{e}")
        return memory

    def makeMemory(self):
        #create/updates memory
        try:
            if not os.path.exists("memory"):os.mkdir("memory")
            for guild in self.guilds_bot_isPart:
                for member in guild.members:
                    if str(member.id) in self.memory:
                        with open(os.path.join("memory",f"{guild.name}#{member.id}.txt"),"w") as memberProfile:
                            memberProfile.write(f"username->{member.name}\n")
                            memberProfile.write(f"userID->{member.id}\n")
                            memberProfile.write(f"information->{self.memory[str(member.id)]["information"]}\n")
                            memberProfile.write(f"favouriteSongs->{self.memory[str(member.id)]["favouriteSongs"]}\n")
                    else:
                        with open(os.path.join("memory",f"{guild.name}#{member.id}.txt"),"w") as memberProfile:
                            memberProfile.write(f"username->{member.name}\n")
                            memberProfile.write(f"userID->{member.id}\n")
                            memberProfile.write(f"information->N/A\n")
                            memberProfile.write(f"favouriteSongs->N/A\n")

        except Exception as e:
            print(f"Some error occurred while creating memory for bot :{e}")

    def updateMemory(self,uID=0,u_name ="",u_guild="",info="",favSongdata=""):
        print("Updating memory with data")
        if str(uID) not in self.memory:
            with open(os.path.join("memory", f"{u_guild}#{uID}"), "w") as memberProfile:
                self.memory[str(uID)]["username"] = f"{u_name}"
                memberProfile.write(f"username->{u_name}")
                self.memory[str(uID)]["userID"] = f"{uID}"
                memberProfile.write(f"userID->{uID}")
                if info=="":
                    self.memory[str(uID)]["information"] = "N/A"
                    memberProfile.write(f"information->N/A")
                else:
                    self.memory[str(uID)]["information"] = f"{info},"
                    memberProfile.write(f"information->{info},")
                if favSongdata=="":
                    self.memory[str(uID)]["favouriteSongs"] = ""
                    memberProfile.write(f"favouriteSongs->N/A")
                else:
                    self.memory[str(uID)]["favouriteSongs"] = f"{favSongdata}[/]"
                    memberProfile.write(f"favouriteSongs->{favSongdata}[/]")
            print(f"User was to not in memory.. \n Registered user in memory..")
        else:
            if uID==0:print(f"Invalid USER ID")
            else:
                if not info=="":
                    self.memory[f"{uID}"]["information"] +=f"{info},"
                self.memory[f"{uID}"]["information"] += f""
                if not favSongdata=="":
                    self.memory[f"{uID}"]["favouriteSongs"] += f"{favSongdata}[/]"
                else:self.memory[f"{uID}"]["favouriteSongs"] += f""
            print(f"User memory updated")
        print(self.memory)



    def markDown_users(self):
        # function creates a file channels.txt and under it every user will be registered with some metadata
        """
        User meta_data::
            username#discriminator : {
                id : {user.id},
                isIntroduced : True/False,
                nickName : {user.nick},
                JoinedServer at : {user.joined_at},
            }
        """
        # first check if member exists or not
        for guild in self.guilds_bot_isPart:
            for member in guild.members:
                if member.bot:
                    continue  # doesn't want bots to be recognised as channel members
                with open(os.path.join(f"Discord_guild#{guild.name}.txt"), "a+") as file:
                    file.seek(0); found = any(f"{member.name}" in line for line in file.readlines())
                if found:
                    print(f"{member.name} already exists in database")
                    continue
                print(
                    f"{member.name}#{member.discriminator if member.discriminator != "0" else "N/A"} : {member.id}; {0} ; {member.nick} ; {member.joined_at};\n")
                try:
                    with open(os.path.join(f"Discord_guild#{guild.name}.txt"), "a+") as file:
                        file.write(
                            f"{member.name}#{member.discriminator} : {member.id}; {0} ; {member.nick} ; {member.joined_at};\n")
                except Exception as e:
                    print(f"Error while marking the user :{e}")

    async def markDown_user(self,member, discriminator):  # Whenever new usr joins it should mark_down the new user
        try:  # to handle any exceptions
            #updating memory
            self.updateMemory(member.id,str(member.guild.name))
            self.makeMemory()
            with open(os.path.join(f"Discord_guild#{member.guild.name}.txt"), "a+") as file:
                usersMetadata = file.readlines()
                for user in usersMetadata:  # if user is present then why mark him again?
                    if user.split("#")[0].strip() == member.name.strip():
                        return
                file.write(f"{member.name}#{discriminator} : {member.id}; {0} ; {member.nick} ; {member.joined_at};\n")
        except Exception as e:
            print(f"Error while marking the user:{e}")

    # anonymous function which gets a random line from a text file
    def get_random_line(self, filename, to_name: str):  # anonymous function
        filename = os.path.join(f"{self.bot_name_personality}", filename)
        try:
            with open(filename, 'r', encoding="utf8") as file:
                lines = file.readlines()
        except Exception as e:
            print(f"Error while opening the file :{e}")
        return re.sub(r"sharad", to_name, extract_message(random.choice(lines)).strip(), flags=re.IGNORECASE)

    # function to get messages for user in bot personality representing a bot's mood
    def get_mood_message(self, name: str):  # name variable suggests for whom the lines are for by punnet bhai
        # make it to change mood if required
        moods = ["peace", "fun", "sad", "angry", "happy"]  # bot can have these moods only
        print(f"{self.bot_refer_name}'s mood is {moods[self.mood - 1]}")
        if self.bot_mood_changeAutomatic:  # default case
            if random.randint(0, 10) > random.randint(0, 10):  # changes mood dynamically
                # changing mood
                self.mood = random.randint(1, 5)
                print(f"{self.bot_refer_name}'s mood changed to {moods[self.mood - 1]}")

        mood_message = ""
        if self.mood == 1:  # peace
            mood_message = self.get_random_line(f"peaced_out_{self.bot_name}.txt", name)

        if self.mood == 2:  # fun
            if random.randint(1, 2) == 1:  # game
                mood_message = self.get_random_line(f"suggest_game_message_{self.bot_name}.txt", name)
            else:  # music
                mood_message = self.get_random_line(f"suggest_songs_message_{self.bot_name}.txt", name)

        if self.mood == 3:  # sad
            mood_message = self.get_random_line(f"sad_messages_by_{self.bot_name}.txt", name)

        if self.mood == 4:  # angry
            mood_message = self.get_random_line(f"abusing_message_By_{self.bot_name}.txt", name)

        if self.mood == 5:  # happy
            mood_message = self.get_random_line(f"yahhh_random_message_{self.bot_name}.txt", name)
        # returns the mood message
        return mood_message

    # adding slash commands to bot for the better user experience
    def add_slash_commands(self):
        # Register a slash command 'roast' to roast anyone
        @self.tree.command(name="roast", description="Roasts anyone")
        async def roast(interaction, name: str):  # here is the use of arguments
            print(f"{interaction.user.name} Invoked roast command to roast {name}")
            joke = self.get_random_line(f"roast_jokes_message_{self.bot_name}.txt", name)
            await interaction.response.send_message(joke)

        # changes the mood of the bot from peace to angry
        @self.tree.command(name="change_mood", description=f"Changes {self.bot_refer_name}'s mood dynamically")
        @app_commands.describe(to="Mood is to be changed to -->")
        @app_commands.choices(to=[discord.app_commands.Choice(name="Peace", value="peace"),
                                  discord.app_commands.Choice(name="Fun", value="fun"),
                                  discord.app_commands.Choice(name="Sad", value="sad"),
                                  discord.app_commands.Choice(name="Angry", value="angry"),
                                  discord.app_commands.Choice(name="Happy", value="happy")
                                  ])
        async def change_mood(interaction, to: app_commands.Choice[str]):  # custom mood change
            print(f"{interaction.user.name} Invoked command to change mood to {to.value}")
            if not self.bot_mood_changeAutomatic:
                print(f"Changing {self.bot_refer_name}'s mood to {to.value}")
                self.mood = self.moods.index(to.value) + 1
                await interaction.response.send_message(f"{self.bot_refer_name}'s mood changed to {to.value}")
            else:
                print(f"Refusing user {interaction.user.name} from changing the bot's mood")
                await interaction.response.send_message(
                    f"Sorry You{interaction.user.name} cannot change {self.bot_refer_name}'s mood since it is set to Automatic Mood Change")
                await interaction.channel.send(f"Please use /set_MoodChangeType custom to change mood dynamically")

        # commands to switch between automatic mood change and custom mood change
        @self.tree.command(name="set_mood_change_type",
                           description=f"Set {self.bot_refer_name}'s mood change random/dynamic")
        @app_commands.describe(to="Mood Change automatic/customised -->")
        @app_commands.choices(to=[discord.app_commands.Choice(name="Automatic", value="automatic"),
                                  discord.app_commands.Choice(name="Custom", value="custom")
                                  ])
        async def set_MoodChange(interaction, to: app_commands.Choice[str]):  # cst mood change type
            print(f"Change bot's mood changing type command invoked: by {interaction.user.name}")
            print(f"Changing bot's mood change type to {to.value.capitalize()}")
            if to.value == "automatic":  # mood changing is set to automatic
                self.bot_mood_changeAutomatic = True
                await interaction.response.send_message(f"{self.bot_refer_name}'s mood is set to automatic \n")
            else:
                self.bot_mood_changeAutomatic = False  # mood changing is set to custom
                # by default the custom mood will be happy
                self.mood = 5  # by default mood is set to happy
                await interaction.response.send_message(
                    f"""{self.bot_refer_name}'s mood is set to custom \n please use /change_mood to change {self.bot_refer_name} mood\n
                                                                By default it is set to Happy""")

        # command to change bot to a different personality
        @self.tree.command(name="change_bot", description=f"Changes personality of bot")
        @app_commands.describe(to="Name of the bot personality users want to switch the bot -->")
        @app_commands.choices(to=[discord.app_commands.Choice(name=bot_name, value=bot_name) for bot_name in discord_bots])
        async def change_Bot_personality(interaction, to: app_commands.Choice[str]):
            print(
                f"User {interaction.user.name} is changing the bot personality from {self.bot_name_personality} to {self.bot_name}'s Personality")
            self.bot_name = discord_bots_generalNames[to.value][0]
            self.bot_refer_name = discord_bots_generalNames[to.value][1]
            # defaults
            self.mood = 5  # happy
            self.bot_mood_changeAutomatic = True  # automatic mood Change
            await interaction.response.send_message(f"Current bot's personality is {self.bot_name}'s Personality")

            await interaction.channel.send(f"{giveIntro(self.bot_name)}")
            print(f"User's bot personality is changed ")

        # command to play music on discord
        # command to fetch download link of a YouTube video
        # command to recommend a music if wanted to play then play the recommended song
        # command to get a game = toss a coin , roll a die
        # command to recommend a movies
        # command to see what;s trending on YouTube and get a direct link to the video
        # command to see what was the last video of a from a YouTube channel
        # command to get the lyrics of a song
        # command to use true_caller api to search for a number information
        # command to make a poll
        """command to suggest a song based on user preference 
                edgeCase 1: if user is using this first time
                            --> recommend song based on any other user's preference
                         2: if no user preference is there and user is asking for song recommendation
                            --> then bot will get most trending song on spotify 
                some important functionalities
                1) recommend a song and ask if user likes it or not 
                 --> if user likes keep it in user preference list and if not then keep it in user dislike list
                2) this should go 4 to 5 times per user  thus we will get some data about user preference 
                    which we will use in out spotify song recommended to get similar songs from data base and recommend it to user

        """
        # command to search in using blackbox AI in test.py
        """
            this is a cheat string which will help me customize the ai to give me answers
            {[here you will tell you if response you will give contains code or not or if you are giving me links tell me like this responseContainsCode = True; responseContainLinks = True] after this you will respons me } .i am giving you some text .. after this string #$0$# is you prompt and before that is what i want to feed you to give me resonse here is the text : my firends mother was will. we all gathered there . A doctor was saying his mother .. the doctor said sunaiyna you will be fine. After saying this he went to market to get enjection i and my friend abhishek sat near the enteracne .. the this is that we were thinking that his mother waas very ill but she wasn't and later on she was cured aslo ... #$0$# what was abhishek's mother name ?
        """

        @self.tree.command(name="search", description="Searches overInternet ")
        async def searchInternet(interaction, query: str):
            print(f"{interaction.user.name} invoked command to search internet with q={query}")
            await interaction.response.send_message(f"Generating the request\nHere is what i found")
            print("Updating memory...")
            self.updateMemory(interaction.user.id,interaction.user.name, interaction.user.guild.name, f"{query}")
            preText="""
                You are an advanced AI capable of understanding context and answering questions based on the provided information. The input will contain context followed by a delimiter "#$0$#", 
                and then a specific question. Your task is to analyze the context and provide an accurate answer to the question. If the context does not provide enough information, respond with a general reply based on your knowledge.
                give response in this way ["analyzing context":"accurate answer of prompt related to context"] or ["analyzing internet":"answer to prompt using internet"]
            
            """
            api_response = await self.internet.get_Response(f"{preText},{self.memory[str(interaction.user.id)]["information"]}#$0$#{query}", max_tokens=10, forced_web_search=True)
            if api_response["reference"] is not None:
                api_references = api_response["reference"]
                referenceLinks = ""
                for reference in api_references:
                    referenceLinks = referenceLinks + reference + "\n"
                await interaction.channel.send(f"{referenceLinks}\n")
            if len(api_response["response"]) > 2000: api_response["response"] = api_response["response"][:1997] + "..."
            _response = str(str(api_response["response"]).encode().decode('unicode-escape'))
            await interaction.channel.send(f"{_response}")

            if api_response["lang"] is not None:
                await interaction.channel.send(f"```{api_response["lang"]}\n{api_response["code"]}```")
            self.makeMemory()#write memory to file

    # method to greet the users when he joins
    async def on_member_join(self, member):
        print(f"User named {member.name} joined")
        print("Marking the user user_list")
        discriminator = member.discriminator
        await self.markDown_user(member, discriminator)
        print(f"Greeting {member.name}")
        channel = member.guild.system_channel
        self.interacting_channelID = channel.id

        if channel is not None:
            # mark_down user
            greet = self.get_random_line(f"greeting_user_message_{self.bot_name}.txt", member.name)
            await channel.send(greet)
            await(channel.send(self.get_mood_message(member.name)))

    # method to greet the user when it deletes a message
    async def on_message_delete(self, message):
        # deleter = ""
        try:
            async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id:  # Check if it’s the author’s message
                    deleter = entry.user
                    if (datetime.now(timezone.utc) - entry.created_at).total_seconds() <= 2:
                        print(f"{deleter.name} has deleted a message by {message.author.name}")
                    else:
                        print(f"Message was deleted by the owner {message.author.name}")
                    break
            else:
                deleter = message.author.name
                print(f"Message was deleted by the owner {message.author.name}")

            await message.channel.send(self.get_random_line(f"deleting_message_{self.bot_name}.txt", deleter.name))
            await(message.channel.send(self.get_mood_message(deleter.name)))
        except Exception as e:
            print(f"Error: {e}")

    # function to deal with when anyone messages on the server
    async def on_message(self, message):  # handling events
        self.interacting_channelID = message.channel.id
        if message.author == self.user:
            print(f"Message from {self.bot_refer_name}: {message.content}")
        else:
            # introduce to user if not introduced
            print(f"Message from {message.author.name}: {message.content}")
        if message.author == self.user:
            return

        if any(message.content.lower().startswith(keyword) for keyword in
               "hello hi hey yo hola namaste nameste wake".split()):  # can use fuzzy also to take inputs
            await message.channel.send(
                f'{self.get_random_line(f"greeting_user_message_{self.bot_name}.txt", message.author.name)}')
            if random.randint(1, 10) > random.randint(1, 10):  # wants to give a mood message
                await(message.channel.send(self.get_mood_message(message.author.name)))

        # Ensure that the bot processes any commands in the message
        await self.process_commands(message)

    # function to delete a message
    # function to introduce bot whenever the new channel is created in that channel
    # function to remove a user
    # function to append and remove user preference data for songs
    # store in this way = {user_id};{song_name};{userRating in range (1 to 10)};{No. of times played};{}


class crazy_discord_Bots:
    """Description: This bot depicts a TikTok personality, punnet Superstar.
    He creates nuisances on various social media and is obsessed with likes and videos.
    Key traits:
    1) Does absurd things like eating bizarre items.
    2) Repeats actions non-stop, and when interrupted, reacts aggressively.
    """

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        intents.guilds = True

        # Initialize the bot and set up the commands
        print("Welcome To The Discord Bot World")

        for i, bot_str in zip(range(0, len(discord_bots)), discord_bots):
            print(f"{i + 1}). bot name: {bot_str}\n")
        user_ch = input("Please choose a bot from the above list:")
        # client = punnetSuperstar_behaviour(command_prefix='!', intents=intents) #this was for only single bot
        #adding multiple bot support
        # but till then this is ok...
        client = globals()[f"bot_behaviour"](bot_name=discord_bots_generalNames[discord_bots[int(user_ch) - 1]][0],
                                             bot_general_name=discord_bots_generalNames[discord_bots[int(user_ch) - 1]][
                                                 1], command_prefix='!', intents=intents)
        load_dotenv()  # Load environment variables (ensure your token is in .env)
        client.run(os.getenv("DISCORDTOKEN2"))


if __name__ == '__main__':
    bot = crazy_discord_Bots()
