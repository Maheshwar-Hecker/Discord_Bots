import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os,random,re
from datetime import datetime, timezone


#extracts message for special cases
def extract_message(line):
    # Match number and period, optional spaces, and then the quoted message
    line = re.sub(r'"','',line,flags=re.IGNORECASE)
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

def giveIntro(Bot_name:str):
    with open(os.path.join(f"{Bot_name}_Personality",f"introduction_{Bot_name}"),"r+") as file:
        return file.read()


class bot_behaviour(commands.Bot):
    def __init__(self, bot_name,bot_general_name,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_name = bot_name
        self.bot_refer_name = bot_general_name
        self.bot_name_personality = f"{self.bot_name}_Personality"
        self.moods = ["peace","fun","sad","angry","happy"]
        self.mood = random.randint(1,
                              5)  # if mood ==1 peace, mood ==2 fun(games/music suggestion) , mood ==3 sad ,mood ==4 angry, mood ==5 happy
        # Register commands when the bot starts
        self.add_slash_commands()

    async def on_ready(self):#prints a message when successful login is achieved
        print(f"Logged in as {self.bot_refer_name} in Discord")
        try:
            await self.tree.sync()  # Sync the slash commands with Discord
            print("Slash commands have been synced.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    def get_random_line(self,filename, to_name: str):  # this was common so made it outside any class
        filename = os.path.join(f"{self.bot_name_personality}", filename)
        with open(filename, 'r', encoding="utf8") as file:
            lines = file.readlines()

            return re.sub(r"sharad", to_name, extract_message(random.choice(lines)).strip(), flags=re.IGNORECASE)

    def get_mood_messgae(self,name:str):#name variable suggests for whom the lines are for by punnet bhai
        #make it to change mood if required
        moods = ["peace","fun","sad","angry","happy"]
        print(f"{self.bot_refer_name}'s mood is {moods[self.mood]}")
        if random.randint(0,10)> random.randint(0,10):#changes mood dynamically
            #changing mood
            self.mood = random.randint(1,5)
            print(f"{self.bot_refer_name}'s mood changed to {moods[self.mood]}")

        mood_message = ""
        if self.mood == 1:  # peace
            mood_message=self.get_random_line(f"peaced_out_{self.bot_name}.txt", name)

        if self.mood == 2:  # fun
            if random.randint(1,2)==1:#game
                mood_message = self.get_random_line(f"suggest_game_messgae_{self.bot_name}.txt", name)
            else : #music
                mood_message = self.get_random_line(f"suggest_songs_messgae_{self.bot_name}.txt", name)

        if self.mood == 3:#sad
            mood_message=self.get_random_line(f"sad_messages_by_{self.bot_name}.txt", name)

        if self.mood == 4:  # angry
            mood_message=self.get_random_line(f"punnet_abusing_messgae_{self.bot_name}.txt", name)

        if self.mood == 5:  # happy
            mood_message=self.get_random_line(f"yahhh_random_messgae_{self.bot_name}.txt", name)

        return mood_message

    def add_slash_commands(self):
        # Register a slash command 'roast'
        @self.tree.command(name="roast", description="Roasts anyone")
        async def roast(interaction,name:str):#here is the use of arguments
            print(f"{interaction.user.name} Invoked roast command to roast {name}")
            joke = self.get_random_line(f"roast_jokes_messgae_{self.bot_name}.txt",name)
            await interaction.response.send_message(joke)

        @self.tree.command(name = "change_mood", description=f"Changes {self.bot_refer_name}'s mood dynamically")
        @app_commands.describe(to = "Mood is to be changed to -->")
        @app_commands.choices(to = [discord.app_commands.Choice(name = "Peace",value = "peace"),
                                   discord.app_commands.Choice(name = "Fun",value = "fun"),
                                   discord.app_commands.Choice(name = "Sad",value = "sad"),
                                   discord.app_commands.Choice(name = "Angry",value = "anger"),
                                   discord.app_commands.Choice(name = "Happy",value = "happy")
        ])
        async def change_mood(interaction,to:app_commands.Choice[str]):
            print(f"{interaction.user.name} Invoked command to change mood to {to.value}")
            print(f"Changing {self.bot_refer_name}'s mood to {to.value}")
            self.mood = self.moods.index(to.value)+1
            await interaction.response.send_message(f"{self.bot_refer_name}'s mood changed to {to.value}")


    async def on_member_join(self,member):
        print(f"User named {member.name} joined")
        print(f"Greeting {member.name}")
        channel = member.guild.system_channel

        if channel is not None:
            greet = self.get_random_line(f"greeting_user_messgae_{self.bot_name}.txt",member.name)
            await channel.send(greet)
            await(channel.send(self.get_mood_messgae(member.name)))

    async def on_message_delete(self, message):
        #deleter = ""
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

            await message.channel.send(self.get_random_line(f"deleting_message_{self.bot_name}.txt",deleter.name))
            await(message.channel.send(self.get_mood_messgae(deleter.name)))
        except Exception as e:
            print(f"Error: {e}")

    async def on_message(self, message):#handling events
        if message.author == self.user:
            print(f"Message from {self.bot_refer_name}: {message.content}")
        else:
            print(f"Message from {message.author.name}: {message.content}")
        if message.author == self.user:
            return

        if any(message.content.lower().startswith(keyword)for keyword in "hello hi hey yo hola namaste nameste wake".split()) :
            await message.channel.send(f'{self.get_random_line(f"greeting_user_messgae_{self.bot_name}.txt",message.author.name)}')
            if random.randint(1,10)>random.randint(1,10):#wants to give a mood message
                await(message.channel.send(self.get_mood_messgae(message.author.name)))

        # Ensure that the bot processes any commands in the message
        await self.process_commands(message)

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

        # Initialize the bot and set up the commands
        print("Welcome To The Discord Bot World")
        discord_bots = ["Punnet Superstar", "Titu Mama"]
        discord_bots_generalNames = {
            "Punnet Superstar": ["punnetSuperstar","Punnet Bhai"],
            "Titu Mama": ["tituMama","Mama"]
        }
        for i,bot_str in zip(range(0, len(discord_bots)),discord_bots):
            print(f"{i+1}). bot name: {bot_str}\n")
        user_ch = input("Please choose a bot from the above list:")
        # client = punnetSuperstar_behaviour(command_prefix='!', intents=intents) #this was for only single bot
        #adding multiple bot support
        #will later on introduce a general bot behaviour with basic functionalities which will be able to suppose do /activate punnet_bhai
        #but till then this is ok...
        client = globals()[f"bot_behaviour"](bot_name = discord_bots_generalNames[discord_bots[int(user_ch) -1]][0],bot_general_name = discord_bots_generalNames[discord_bots[int(user_ch) -1]][1],command_prefix='!', intents=intents)
        load_dotenv()  # Load environment variables (ensure your token is in .env)
        client.run(os.getenv("DISCORDTOKEN2"))

if __name__ == '__main__':
    bot = crazy_discord_Bots()
