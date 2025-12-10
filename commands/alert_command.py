import discord
import os
from discord.ext import commands
from discord import app_commands
from database.alerts_db import initialize_db, add_alert, get_user_alerts, remove_alert, delete_alert, get_alert_count, clear_user_alert, get_all_active_alerts

class Alert_Command(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        initialize_db()
    
    def alert_add(self, ticker: str, price: float, type: str):
        pass