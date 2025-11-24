import discord
import os
from dotenv import load_dotenv

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    client = Client(intents=intents)
    load_dotenv()
    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()
