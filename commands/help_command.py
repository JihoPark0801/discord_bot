import discord
from discord.ext import commands
from discord import app_commands
import os

class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Show all available commands and features")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def help(self, interaction: discord.Interaction):
        # Create main embed
        embed = discord.Embed(
            title="📚 Stock Trading Bot - Command Guide",
            description="Your complete virtual stock trading assistant with portfolio management, price alerts, and more!",
            color=discord.Color.blue()
        )
        
        # Portfolio Commands
        embed.add_field(
            name="💼 Portfolio Management",
            value=(
                "`/portfolio_start` - Create your trading account ($100,000 starting balance)\n"
                "`/buy <ticker> <quantity>` - Purchase stocks (e.g., `/buy AAPL 10`)\n"
                "`/sell <ticker> <quantity>` - Sell stocks (e.g., `/sell TSLA 5`)\n"
                "`/portfolio` - View your holdings with P/L\n"
                "`/balance` - Check cash and total account value\n"
                "`/history [ticker]` - View transaction history\n"
                "`/portfolio_reset` - Reset to $100,000"
            ),
            inline=False
        )
        
        # Watchlist Commands
        embed.add_field(
            name="👀 Watchlist",
            value=(
                "`/watchlist_add <ticker>` - Add stock to watchlist\n"
                "`/watchlist_remove <ticker>` - Remove from watchlist\n"
                "`/watchlist` - View watchlist with current prices\n"
                "`/watchlist_clear` - Clear entire watchlist"
            ),
            inline=False
        )
        
        # Alert Commands
        embed.add_field(
            name="🔔 Price Alerts",
            value=(
                "`/alert_add <ticker> <price> <type>` - Set price alert\n"
                "  • Types: `above` or `below`\n"
                "  • Example: `/alert_add AAPL 160 above`\n"
                "`/alert_list` - View all active alerts\n"
                "`/alert_remove <ticker> <price>` - Remove specific alert\n"
                "`/alert_clear` - Clear all alerts"
            ),
            inline=False
        )
        
        # Utility Commands
        embed.add_field(
            name="🛠️ Utilities",
            value=(
                "`/stock <ticker>` - Get current stock price\n"
                "`/dashboard` - Get link to web dashboard\n"
                "`/help` - Show this help message"
            ),
            inline=False
        )
        
        # Web Dashboard Info
        embed.add_field(
            name="🌐 Web Dashboard",
            value=(
                "Access your portfolio dashboard with:\n"
                "• Interactive charts and graphs\n"
                "• Real-time portfolio tracking\n"
                "• Watchlist and alerts overview\n"
                "• Login with Discord (secure OAuth)\n"
                "\nUse `/dashboard` to get the link!"
            ),
            inline=False
        )
        
        # Tips & Info
        embed.add_field(
            name="💡 Tips",
            value=(
                "• Start with `/portfolio_start` to create your account\n"
                "• All prices are real-time market data\n"
                "• Use whole shares only (no fractional)\n"
                "• Alerts check every 5 minutes\n"
                "• Your data is private and secure"
            ),
            inline=False
        )
        
        embed.set_footer(text="Happy trading! 📈 | All trading is virtual with no real money")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user else None)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))