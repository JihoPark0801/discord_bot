import discord
import os
from discord.ext import commands
from discord import app_commands
from database.portfolio_db import *
from api.stocks import get_stock_price, get_percentage_change

class PortfolioCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="portfolio_start", description="Creates your virtual portfolio account")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def portfolio_start(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        valid = user_exists(user_id)

        if valid:
            await interaction.response.send_message("You already have an account", ephemeral = True)
        else:
            success = create_user(user_id, 100000.0)
            if success:
                embed = discord.Embed(
                    title = "Portfolio Created!",
                    description = f"Welcome to virtual trading!\nStarting balance: **$100,000.00**",
                    color = discord.Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("Error creating account", ephemeral=True)

    @app_commands.command(name="buy", description="Buys a stock of your choice")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def buy(self, interaction: discord.Interaction, ticker: str, quantity: int):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)

        user_has_account = user_exists(user_id)

        if not user_has_account:
            await interaction.followup.send("You do not have an existing account. Try running /portfolio_start first")
            return
        
        if (quantity <= 0):
            await interaction.followup.send("Quantity is not a positive integer")
            return
        
        current_price = get_stock_price(ticker)

        if current_price is None:
            await interaction.followup.send("Invalid ticker")
            return
        
        total_cost = current_price * quantity
        user_info = get_user(user_id)
        cash_balance = user_info[0]
        if (total_cost > cash_balance):
            await interaction.followup.send("Not enough cash")
            return
        
        new_cash_balance = cash_balance - total_cost
        update_cash_balance(user_id, new_cash_balance)
        add_or_update_position(user_id, ticker, quantity, current_price)
        record_transaction(user_id, ticker, "buy", quantity, current_price, total_cost)
        
        embed = discord.Embed(
            title="✅ Purchase Successful",
            description=f"Bought **{quantity}** shares of **{ticker.upper()}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Price per Share", value=f"${current_price:.2f}", inline=True)
        embed.add_field(name="Total Cost", value=f"${total_cost:.2f}", inline=True)
        embed.add_field(name="Cash Remaining", value=f"${new_cash_balance:.2f}", inline=True)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(PortfolioCommand(bot))