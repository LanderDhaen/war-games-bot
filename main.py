import discord
from discord.ext import commands

from config import TOKEN


class WarGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)


bot = WarGamesBot()

bot.run(TOKEN)
