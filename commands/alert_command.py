import discord
import os
from api.stocks import get_stock_price
from discord.ext import commands
from discord import app_commands
from database.alerts_db import initialize_db, add_alert, get_user_alerts, remove_alert, delete_alert, get_alert_count, clear_user_alert

class Alert_Command(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        initialize_db()

    @app_commands.command(name="alert_add", description="Add a price alert")
    @app_commands.choices(type=[
    app_commands.Choice(name="Above", value="above"),
    app_commands.Choice(name="Below", value="below")])
    async def alert_add(self, interaction: discord.Interaction, ticker: str, target_price: float, type: str):
        await interaction.response.defer(ephemeral=True)
        ticker = ticker.upper()
        user_id = str(interaction.user.id)

        if get_alert_count(user_id) >= 10:
            await interaction.followup.send("Reached alert limit")
            return
        
        current_price = get_stock_price(ticker)

        if current_price is None:
            await interaction.followup.send("Invalid ticker")
            return
        
        if (type == "below" and current_price <= target_price):
            await interaction.followup.send(f"{ticker} is already below that price")
            return

        elif (type == "above" and current_price >= target_price):
            await interaction.followup.send(f"{ticker} is already above that price")
            return
        
        valid = add_alert(user_id, ticker, target_price, type)
        if valid:
            await interaction.followup.send(f"Success!")

        else:
            await interaction.followup.send("Duplicate alert already exists")
    
    @app_commands.command(name="alert_list", description="Shows a list of all your alerts")
    async def alerts_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        user_alerts = get_user_alerts(user_id)

        if not user_alerts:
            await interaction.followup.send("No Active Alerts")
            return

        embed = discord.Embed(title="Alert List", description="List of user alerts", color=discord.Color.blue())

        for alerts in user_alerts:
            ticker, target_price, alert_type, created_at = alerts
            current_price = get_stock_price(ticker)
            if current_price is None:
                embed.add_field(name=f"{ticker} - {alert_type} ${target_price:.2f}", value="Current Price: N/A", inline=False)
            else:
                distance_from_target = abs(current_price - target_price)
                embed.add_field(name=f"{ticker} - {alert_type} ${target_price:.2f}", value=f"Current Price: ${current_price:.2f} (${distance_from_target:.2f} away from target)", inline=False)

        embed.set_footer(text=f"Total Alerts: {len(user_alerts)}")
        await interaction.followup.send(embed=embed)
