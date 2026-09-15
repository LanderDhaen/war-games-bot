import discord


class MissingConfigurationEmbed(discord.Embed):
    def __init__(self, *, is_admin: bool):
        description = (
            "This server is not yet configured. Use `/setup server` to get started."
            if is_admin
            else "This server is not yet configured. Please contact an administrator."
        )

        super().__init__(
            title="Missing Configuration",
            description=description,
            color=discord.Color.red(),
        )


class MissingHostRoleEmbed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="Missing Host Role",
            description="You need the configured host role to use this command.",
            color=discord.Color.red(),
        )


class InvalidGuildConfigurationEmbed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="Invalid Configuration",
            description=(
                "That role or channel no longer exists in this server. "
                "Use `/setup server` to reconfigure the settings."
            ),
            color=discord.Color.red(),
        )


class InvalidSeasonStartEmbed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="Invalid Configuration",
            description=(
                "This is not a valid date and time. Please use the ISO format, "
                "for example `2026-09-20 19:00`."
            ),
            color=discord.Color.red(),
        )
