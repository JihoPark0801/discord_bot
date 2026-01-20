import discord
import os
from discord.ext import commands
from discord import app_commands
from database.portfolio_db import *
from api.stocks import get_stock_price, get_percentage_change

class PortfolioCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        initialize_portfolio_db()

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
        ticker = ticker.upper()

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
        embed.add_field(name="Price per Share", value=f"${current_price:,.2f}", inline=True)
        embed.add_field(name="Total Cost", value=f"${total_cost:,.2f}", inline=True)
        embed.add_field(name="Cash Remaining", value=f"${new_cash_balance:,.2f}", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sell", description="Sells a stock of your choice")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def sell(self, interaction: discord.Interaction, ticker: str, quantity: int):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        ticker = ticker.upper()
        user_has_account = user_exists(user_id)

        if not user_has_account:
            await interaction.followup.send("You do not have an existing account. Try running /portfolio_start first")
            return
    
        if quantity <= 0:
            await interaction.followup.send("Quantity must be a positive integer")
            return
       
        current_price = get_stock_price(ticker)
        if current_price is None:
            await interaction.followup.send("Invalid ticker")
            return
        
        user_position = get_position(user_id, ticker)
        if not user_position:
            await interaction.followup.send(f"You do not own any shares of {ticker}")
            return
        
        shares_owned = user_position[0]

        if (quantity > shares_owned):
            await interaction.followup.send("You cannot sell more shares than you own")
            return
        proceeds =  current_price * quantity
        user_info = get_user(user_id)
        cash_balance = user_info[0]
        new_cash_balance = proceeds + cash_balance
        update_cash_balance(user_id, new_cash_balance)
        reduce_or_remove_position(user_id, ticker, quantity)
        record_transaction(user_id, ticker, "sell", quantity, current_price, proceeds)

        avg_cost = user_position[1]
        profit_loss = (current_price - avg_cost) * quantity
        percent_change = (profit_loss / (avg_cost * quantity)) * 100

        color = discord.Color.green() if profit_loss >= 0 else discord.Color.red()
        pl_emoji = "📈" if profit_loss >= 0 else "📉"

        embed = discord.Embed(
            title="✅ Sale Successful",
            description=f"Sold **{quantity}** shares of **{ticker}**",
            color=color
        )
        embed.add_field(name="Price per Share", value=f"${current_price:,.2f}", inline=True)
        embed.add_field(name="Total Proceeds", value=f"${proceeds:,.2f}", inline=True)
        embed.add_field(name="Cash Balance", value=f"${new_cash_balance:,.2f}", inline=True)
        embed.add_field(name=f"{pl_emoji} Profit/Loss", value=f"${profit_loss:,.2f} ({percent_change:+,.2f}%)", inline=False)

        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="portfolio", description="Displays your virtual portfolio holdings")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def display_portfolio(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)

        user_has_account = user_exists(user_id)
        if not user_has_account:
            await interaction.followup.send("You do not have an existing account. Try running /portfolio_start first")
            return  
        
        all_holdings = get_user_portfolio(user_id)
        user_info = get_user(user_id)
        cash_balance = user_info[0]
        starting_balance = user_info[1]
        
        # If no holdings, show cash only
        if not all_holdings:
            embed = discord.Embed(
                title="📊 Your Portfolio",
                description="You don't own any stocks yet!",
                color=discord.Color.blue()
            )
            embed.add_field(name="💰 Cash Balance", value=f"${cash_balance:,.2f}", inline=False)
            embed.add_field(name="Total Account Value", value=f"${cash_balance:,.2f}", inline=False)
            await interaction.followup.send(embed=embed)
            return
        
        # Calculate portfolio value
        total_portfolio_value = 0
        total_cost_basis = 0
        
        # Create embed
        embed = discord.Embed(
            title="📊 Your Portfolio",
            color=discord.Color.blue()
        )
        
        # Add each holding as a field
        for holding in all_holdings:
            ticker = holding[0]
            quantity = holding[1]
            avg_cost = holding[2]
            
            # Get current price
            current_price = get_stock_price(ticker)
            
            if current_price is None:
                # If API fails, show N/A
                embed.add_field(
                    name=f"📈 {ticker}",
                    value=f"**Quantity:** {quantity}\n**Avg Cost:** ${avg_cost:,.2f}\n**Current:** N/A",
                    inline=False
                )
                continue
            
            # Calculate values
            current_value = quantity * current_price
            cost_basis = quantity * avg_cost
            profit_loss = current_value - cost_basis
            percent_change = (profit_loss / cost_basis) * 100
            
            # Add to totals
            total_portfolio_value += current_value
            total_cost_basis += cost_basis
            
            # Color code P/L
            pl_emoji = "📈" if profit_loss >= 0 else "📉"
            pl_text = f"+${profit_loss:,.2f}" if profit_loss >= 0 else f"-${abs(profit_loss):,.2f}"
            
            # Add field for this stock
            embed.add_field(
                name=f"{pl_emoji} {ticker}",
                value=f"**Qty:** {quantity} @ ${avg_cost:,.2f}\n**Current:** ${current_price:,.2f}\n**Value:** ${current_value:,.2f}\n**P/L:** {pl_text} ({percent_change:+,.2f}%)",
                inline=True
            )
        
        # Calculate overall stats
        total_account_value = total_portfolio_value + cash_balance
        overall_pl = total_account_value - starting_balance
        overall_percent = (overall_pl / starting_balance) * 100
        
        # Set description with overall stats
        pl_emoji = "📈" if overall_pl >= 0 else "📉"
        embed.description = f"**Total Account Value:** ${total_account_value:,.2f}\n{pl_emoji} **Overall P/L:** ${overall_pl:+,.2f} ({overall_percent:+,.2f}%)"
        
        # Footer with cash
        embed.set_footer(text=f"💰 Cash: ${cash_balance:,.2f} | 📊 Invested: ${total_portfolio_value:,.2f}")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="balance", description="Show your account balance and summary")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        
        # Check if user exists
        if not user_exists(user_id):
            await interaction.followup.send("You do not have an existing account. Try running /portfolio_start first")
            return
        
        # Get user info
        user_info = get_user(user_id)
        cash_balance = user_info[0]
        starting_balance = user_info[1]
        
        # Get all holdings to calculate invested amount
        all_holdings = get_user_portfolio(user_id)
        
        total_cost_basis = 0
        total_current_value = 0
        
        # Calculate totals
        for holding in all_holdings:
            ticker = holding[0]
            quantity = holding[1]
            avg_cost = holding[2]
            
            cost_basis = quantity * avg_cost
            total_cost_basis += cost_basis
            
            # Get current value
            current_price = get_stock_price(ticker)
            if current_price:
                total_current_value += quantity * current_price
            else:
                # If API fails, use cost basis as estimate
                total_current_value += cost_basis
        
        # Calculate overall stats
        total_account_value = cash_balance + total_current_value
        overall_pl = total_account_value - starting_balance
        overall_percent = (overall_pl / starting_balance) * 100
        
        # Create embed
        color = discord.Color.green() if overall_pl >= 0 else discord.Color.red()
        
        embed = discord.Embed(
            title="💰 Account Balance",
            color=color
        )
        
        embed.add_field(name="Cash Balance", value=f"${cash_balance:,.2f}", inline=True)
        embed.add_field(name="Invested (Cost Basis)", value=f"${total_cost_basis:,.2f}", inline=True)
        embed.add_field(name="Portfolio Value", value=f"${total_current_value:,.2f}", inline=True)
        embed.add_field(name="Total Account Value", value=f"${total_account_value:,.2f}", inline=False)
        
        pl_emoji = "📈" if overall_pl >= 0 else "📉"
        embed.add_field(
            name=f"{pl_emoji} Overall Profit/Loss",
            value=f"${overall_pl:+,.2f} ({overall_percent:+,.2f}%)",
            inline=False
        )
        
        embed.set_footer(text=f"Starting Balance: ${starting_balance:,.2f}")
        
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="history", description="View your transaction history")
    @app_commands.describe(ticker="Optional: Filter by specific ticker")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def history(self, interaction: discord.Interaction, ticker: str = None):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        
        # Check if user exists
        if not user_exists(user_id):
            await interaction.followup.send("You do not have an existing account. Try running /portfolio_start first")
            return
        
        # Get transactions (optionally filtered)
        if ticker:
            ticker = ticker.upper()
            transactions = get_user_transactions(user_id, ticker)
            title = f"📜 Transaction History - {ticker}"
        else:
            transactions = get_user_transactions(user_id)
            title = "📜 Transaction History"
        
        # Check if no transactions
        if not transactions:
            await interaction.followup.send(f"No transactions found{' for ' + ticker if ticker else ''}")
            return
        
        # Create embed
        embed = discord.Embed(
            title=title,
            color=discord.Color.blue()
        )
        
        # Add each transaction as a field
        # Limit to most recent 25 (Discord embed limit is 25 fields)
        for i, txn in enumerate(transactions[:25]):
            # txn tuple: (ticker, transaction_type, quantity, price, total_cost, timestamp)
            txn_ticker = txn[0]
            txn_type = txn[1]
            quantity = txn[2]
            price = txn[3]
            total = txn[4]
            timestamp = txn[5]
            
            # Format timestamp (just date, not full timestamp)
            # timestamp format: '2025-01-20 14:30:00'
            date = timestamp.split(' ')[0]  # Gets '2025-01-20'
            
            # Emoji and color based on type
            emoji = "🟢" if txn_type == "buy" else "🔴"
            
            # Field name
            field_name = f"{emoji} {txn_type.upper()} - {txn_ticker}"
            
            # Field value
            field_value = f"**Qty:** {quantity} @ ${price:,.2f}\n**Total:** ${total:,.2f}\n**Date:** {date}"
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=True
            )
        
        # Footer
        if len(transactions) > 25:
            embed.set_footer(text=f"Showing 25 of {len(transactions)} transactions")
        else:
            embed.set_footer(text=f"Total transactions: {len(transactions)}")
        
        await interaction.followup.send(embed=embed)
    @app_commands.command(name="portfolio_reset", description="Reset your portfolio to starting balance (deletes all holdings)")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def portfolio_reset(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        # Check if user exists
        if not user_exists(user_id):
            await interaction.response.send_message(
                "You do not have an existing account. Try running /portfolio_start first",
                ephemeral=True
            )
            return
        
        # Reset the portfolio
        success = reset_portfolio(user_id)
        
        if success:
            embed = discord.Embed(
                title="🔄 Portfolio Reset",
                description="Your portfolio has been reset!",
                color=discord.Color.orange()
            )
            embed.add_field(name="Cash Balance", value="$100,000.00", inline=True)
            embed.add_field(name="Holdings", value="Cleared", inline=True)
            embed.add_field(name="Transaction History", value="Cleared", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "Error resetting portfolio",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(PortfolioCommand(bot))