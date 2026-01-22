import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import os

class DashboardView(ui.View):
    def __init__(self, dashboard_url):
        super().__init__(timeout=None)
        # Add button that links to dashboard
        button = ui.Button(
            label="Open Dashboard",
            style=discord.ButtonStyle.link,
            url=dashboard_url,
            emoji="📊"
        )
        self.add_item(button)

class DashboardCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Change this to your deployed URL later
        # For now, use local
        self.dashboard_url = "http://127.0.0.1:5001"
    
    @app_commands.command(name="dashboard", description="Access your web portfolio dashboard")
    @app_commands.guilds(discord.Object(id=os.getenv('DISCORD_GUILD_ID')))
    async def dashboard(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📊 Portfolio Dashboard",
            description="View your portfolio with detailed charts and analytics!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="✨ Features",
            value="• Real-time portfolio value\n• Interactive charts\n• Watchlist tracking\n• Active price alerts\n• Profit/Loss calculations",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Secure Login",
            value="Login with your Discord account - no passwords needed!",
            inline=False
        )
        
        embed.set_footer(text="Click the button below to open your dashboard")
        
        view = DashboardView(self.dashboard_url)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DashboardCommand(bot))