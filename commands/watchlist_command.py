import discord
from discord.ext import commands
from discord import app_commands
from api.stocks import get_stock_price  
from database.watchlist_db import add_to_watchlist, remove_from_watchlist, get_watchlist, initialize_db, clear_watchlist
import os

class WatchlistCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        initialize_db()
    
    @app_commands.command(name="watchlist_add", description="Add a stock ticker to your watchlist.")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def add_watchlist(self, interaction: discord.Interaction, ticker: str):
        try:    
            await interaction.response.defer(ephemeral=True)
            user_id = str(interaction.user.id)
            ticker = ticker.upper()
            ticker_exists = get_stock_price(ticker)

            if ticker_exists is not None:
                valid = add_to_watchlist(user_id, ticker)
                if valid:
                    await interaction.followup.send("Successfully added to watchlist")
                else:
                    await interaction.followup.send(f"{ticker} already in watchlist")
            else:
                await interaction.followup.send(f"Invalid ticker: {ticker}")
        except Exception as e:
            await interaction.followup.send("An error has occured. Please try again.")
    @app_commands.command(name="watchlist_remove", description= "Remove a stock from your watchlist")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def remove_watchlist(self, interaction: discord.Interaction, ticker: str):
        try:
            await interaction.response.defer(ephemeral=True)
            user_id = str(interaction.user.id)
            ticker = ticker.upper()
            valid_removal = remove_from_watchlist(user_id, ticker)

            if valid_removal:
                await interaction.followup.send(f"{ticker} succesfully removed from watchlist")
            
            else:
                await interaction.followup.send(f"{ticker} not in your watchlist")
        except:
            await interaction.followup.send("An error has occured. Please try again.")
   
    @app_commands.command(name="watchlist", description="Shows your watchlist")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def watchlist(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        ticker_list = get_watchlist(user_id)
        if not ticker_list:
            await interaction.followup.send("Your watchlist is empty")
            return
        embed = discord.Embed(title="Watchlist", description="Current stock prices", color=discord.Color.blue())

        for ticker in ticker_list:
            stock_price = get_stock_price(ticker)
            price_display = f"${stock_price:.2f}" if stock_price else "N/A"
            embed.add_field(name=f"{ticker}", value=price_display, inline=True)
        
        embed.set_footer(text=f"Total stocks: {len(ticker_list)}")
        embed.timestamp = discord.utils.utcnow()
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="watchlist_clear", description="Clears your watchlist")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def watchlist_clear(self, interaction: discord.Integration):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        stocks_removed = clear_watchlist(user_id)
        if stocks_removed == 0:
            await interaction.followup.send("Watchlist is already empty")
            return

        await interaction.followup.send(f"{stocks_removed} were removed")


async def setup(bot: commands.Bot):
    await bot.add_cog(WatchlistCommand(bot))