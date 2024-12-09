import discord
from discord.ext import commands
from dotenv import load_dotenv
import os,random,re
from datetime import datetime, timezone


name = "Puneet Super_Star"  # This can be an array for different bots if needed

#extracts message for speacial cases
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




class PuneetSuperstar_behaviour(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_slash_commands()  # Register commands when the bot starts
        self.bot_name = "punnetSuperStar"
        self.bot_name_personality = "punnetSuperStar_Personality"
        self.mood = random.randint(1,
                              5)  # if mood ==1 peace, mood ==2 fun(games/music suggestion) , mood ==3 sad ,mood ==4 angry, mood ==5 happy

    async def on_ready(self):
        print(f"Logged in as {self.user.name} in Discord")
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
        print(f"Punnet bhai's mood is {self.mood}")
        if random.randint(0,10)> random.randint(0,10):#changes mood dynamically
            #changing mood
            self.mood = random.randint(1,5)
            print(f"Punnet bhai's mood changed to {self.mood}")

        mood_message = ""
        if self.mood == 1:  # peace
            mood_message=self.get_random_line("peaced_out_puneetSuperstar.txt", name)

        if self.mood == 2:  # fun
            if random.randint(1,2)==1:#game
                mood_message = self.get_random_line("suggest_game_messgae_puneetSuperstar.txt", name)
            else : #music
                mood_message = self.get_random_line("suggest_songs_messgae_puneetSuperstar.txt", name)

        if self.mood == 3:#sad
            mood_message=self.get_random_line("sad_messages_by_puneetSuperstar.txt", name)

        if self.mood == 4:  # angry
            mood_message=self.get_random_line("punnet_abusing_messgae_puneetSuperstar.txt", name)

        if self.mood == 5:  # happy
            mood_message=self.get_random_line("yahhh_random_messgae_puneetSuperstar.txt", name)

        return mood_message

    def add_slash_commands(self):
        # Register a slash command 'hello'
        @self.tree.command(name="roast", description="Roasts anyone")
        async def roast(interaction,name:str):#here is the use of arguments
            print(f"{interaction.user.name} Invoked roast command to roast {name}")
            joke = self.get_random_line("roast_jokes_messgae_puneetSuperstar.txt",name)
            await interaction.response.send_message(joke)


    async def on_member_join(self,member):
        print(f"User named {member.name} joined")
        print(f"Greeting {member.name}")
        channel = member.guild.system_channel

        if channel is not None:
            greet = self.get_random_line("greeting_user_messgae_puneetSuperstar.txt",member.name)
            await channel.send(greet)
            await(channel.send(self.get_mood_messgae(member.name)))

    async def on_message_delete(self, message):
        deleter = ""
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

            await message.channel.send(self.get_random_line("deleting_message_puneetSuperstar.txt",deleter.name))
            await(message.channel.send(self.get_mood_messgae(deleter.name)))
        except Exception as e:
            print(f"Error: {e}")


        # You can add more slash commands here

    async def on_message(self, message):#handling events
        print(f"Message from {message.author.name}: {message.content}")
        if message.author == self.user:
            return

        if any(message.content.lower().startswith(keyword)for keyword in "hello hi yo hola namaste nameste wake".split()) :
            await message.channel.send(f'{self.get_random_line("greeting_user_messgae_puneetSuperstar.txt",message.author.name)}')
            if random.randint(1,10)>random.randint(1,10):#wants to give a mood message
                await(message.channel.send(self.get_mood_messgae(message.author.name)))

        # Ensure that the bot processes any commands in the message
        await self.process_commands(message)

class Puneet_Superstar:
    '''Description: This bot depicts a TikTok personality, Puneet Superstar.
    He creates nuisances on various social media and is obsessed with likes and videos.
    Key traits:
    1) Does absurd things like eating bizarre items.
    2) Repeats actions non-stop, and when interrupted, reacts aggressively.
    '''
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        # Initialize the bot and set up the commands
        client = PuneetSuperstar_behaviour(command_prefix='!', intents=intents)

        load_dotenv()  # Load environment variables (ensure your token is in .env)
        client.run(os.getenv("DISCORDTOKEN2"))

if __name__ == '__main__':
    bot = Puneet_Superstar()
