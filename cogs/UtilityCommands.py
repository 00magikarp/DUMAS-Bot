import discord
from discord.ext import commands


# noinspection PyUnresolvedReferences
class UtilityCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="ping",
        description="Check latency of bot"
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        """
        Check the latency of the bot.

        :param interaction: The interaction object.
        """
        await interaction.response.send_message(
            f"""🏓 Pong!
{self.bot.latency * 1000:.1f}ms"""
        )

    @discord.app_commands.command(
        name="help",
        description="Help for the bot."
    )
    async def help(self, interaction: discord.Interaction) -> None:
        """
        Help for the bot.

        :param interaction: The interaction object.
        """


async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
