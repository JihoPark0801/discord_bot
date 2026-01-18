import discord
import os
from api.stocks import get_stock_price
from discord.ext import commands, tasks
from discord import app_commands
from database.alerts_db import initialize_db, add_alert, get_user_alerts, remove_alert, delete_alert, get_alert_count, clear_user_alerts, get_all_active_alerts

class AlertCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        initialize_db()
        self.check_alerts_task.start()
    
    def cog_unload(self):
        self.check_alerts_task.cancel()

    @tasks.loop(minutes=5)
    async def check_alerts_task(self):
        try:
            alerts = get_all_active_alerts()

            if not alerts:
                print("No active alerts")
                return
            
            alerts_by_ticker = {}
            for alert in alerts:
                id = alert[0]
                user_id = alert[1]
                ticker = alert[2]
                target_price = alert[3]
                alert_type = alert[4]

                if ticker not in alerts_by_ticker:
                    alerts_by_ticker[ticker] = []
                
                alerts_by_ticker[ticker].append({
                    'id': id,
                    'user_id': user_id,
                    'ticker': ticker,
                    'target_price': target_price,
                    'alert_type': alert_type
                })
            
        except Exception as e:
            print(f"Alert task error: {e}")
    
    @check_alerts_task.before_loop
    async def before_check_alerts(self):
        await self.bot.wait_until_ready()
        print("Alert checking task started!")
        

    @app_commands.command(name="alert_add", description="Add a price alert")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
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
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
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
    
    @app_commands.command(name="alert_remove", description="Removes an existing alert")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def alert_remove(self, interaction: discord.Interaction, ticker: str, price: float):
        ticker = ticker.upper()
        user_id = str(interaction.user.id)
        removal = remove_alert(user_id, ticker, price)

        if removal:
            await interaction.response.send_message(f"✅ Removed alert for {ticker} at ${price:.2f}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ No alert found for {ticker} at ${price:.2f}",ephemeral=True)

    @app_commands.command(name="alert_clear", description="Clear all your alerts")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def alert_clear(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        count = clear_user_alerts(user_id)

        if count == 0:
            await interaction.response.send_message("No alerts to clear", ephemeral=True)
        else:
            await interaction.response.send_message(f"Cleared {count} alerts", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AlertCommand(bot))