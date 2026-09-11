from typing import Literal

import discord

from discord import app_commands
from discord.ext import commands
from config import TOKEN, HOST_ROLE_ID
from data.database import configure_guild, create_tables, get_guild

class WarGamesBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await create_tables() 

bot = WarGamesBot()

@bot.command(name="sync")
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, scope: Literal["global", "guild"] = "guild"):
    if scope == "guild":
        bot.tree.copy_global_to(guild=ctx.guild)
        synced  = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"{len(synced)} command(s) synced for {ctx.guild.name}.")
    elif scope == "global":
        synced = await bot.tree.sync()
        await ctx.send(f"{len(synced)} command(s) synced globally.")

@app_commands.command(name="setup", description="Configure your server for War Games.")
@app_commands.describe(host_role="The role that will be assigned to hosts.", result_channel="The channel where game results will be posted.")
@app_commands.rename(host_role="host-role", result_channel="result-channel")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guild_only()
async def setup(interaction: discord.Interaction, host_role: discord.Role, result_channel: discord.TextChannel):

    guild = await configure_guild(interaction.guild.id, host_role.id, result_channel.id)

    await interaction.response.send_message(f"Setting up your server for War Games with host role {guild.host_role_id} and result channel {guild.result_channel_id}.", ephemeral=True)

bot.tree.add_command(setup)


bot.run(TOKEN)

