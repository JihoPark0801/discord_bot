import discord
from api.stocks import get_stock_price, get_percentage_change
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
        ticker_symbol = ticker_symbol.upper()
        price = get_stock_price(ticker_symbol)
        percent_change = get_percentage_change(ticker_symbol)
        embed = discord.Embed(title=f"{ticker_symbol} Stock Information", color=discord.Color.blue())

        embed.add_field(name="Current Price", value=f"${price:.2f}" if price is not None else "N/A", inline=True)
        embed.add_field(name="24h Change", value=f"{percent_change:.2f}%" if percent_change is not None else "N/A", inline=True)    

        embed.timestamp = discord.utils.utcnow()
        
        if price is not None:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Could not retrieve data for ticker symbol: {ticker_symbol.upper()}")

async def setup(bot: commands.Bot):
    await bot.add_cog(StockCommand(bot))