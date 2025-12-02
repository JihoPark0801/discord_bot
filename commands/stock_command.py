import discord
from api.stocks import get_stock_price
from discord.ext import commands
from discord import app_commands
import os


class StockCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stock", description="Get the current stock price for a given ticker symbol.")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def stock(self, interaction: discord.Interaction, ticker_symbol: str):
        await interaction.response.defer()  # Acknowledge the command to avoid timeout
        price = get_stock_price(ticker_symbol)
        
        if price is not None:
            await interaction.followup.send(f"The current price of {ticker_symbol.upper()} is ${price:.2f}")
        else:
            await interaction.followup.send(f"Could not retrieve data for ticker symbol: {ticker_symbol.upper()}")

async def setup(bot: commands.Bot):
    await bot.add_cog(StockCommand(bot))