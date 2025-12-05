import discord
from discord.ext import commands
from discord import app_commands
from api.stocks import get_stock_price  
from database.watchlist_db import add_to_watchlist, remove_from_watchlist, get_watchlist, initialize_db
import os

class WatchlistCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        initialize_db()
    
    @app_commands.command(name="add_watchlist", description="Add a stock ticker to your watchlist.")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def add_watchlist(self, interaction: discord.Interaction, ticker: str):
        user_id = str(interaction.user.id)
        ticker = ticker.upper()
        ticker_exists = get_stock_price()

        if ticker_exists is not None:
            add_to_watchlist(user_id, ticker)
        