import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        try:
            guild = discord.Object(id=os.getenv('DISCORD_GUILD_ID'))
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')
    
    async def setup_hook(self):
        for filename in os.listdir('./commands'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await self.load_extension(f'commands.{filename[:-3]}')
                    print(f'Loaded extension: {filename}')
                except Exception as e:
                    print(f'Failed to load extension {filename}: {e}')


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    client = Client(command_prefix="!", intents=intents)
    load_dotenv()
    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()
