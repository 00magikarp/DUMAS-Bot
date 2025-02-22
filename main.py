import asyncio
import os

import discord
import dotenv
from discord.ext import commands
from extras.CustomLogger import CustomLogger

logger = CustomLogger(CustomLogger.INFO)

dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all(), case_insensitive=True)
testGuild = discord.Object(id=os.getenv('TEST_GUILD'))
ownerId = os.getenv('OWNER_ID')


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename.endswith("Commands.py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            logger.log(f"Loaded cogs.{filename}", logger.INFO)


@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: discord.app_commands.Command) -> None:
    server = interaction.guild.name
    user = interaction.user

    logger.log(f"[[{user}]] RAN [[{command.name}]] IN [[{server}]]", logger.INFO)


@bot.event
async def on_ready() -> None:
    await bot.wait_until_ready()
    logger.log(f"Logged in as: {bot.user}", logger.INFO)


@bot.command()
async def syncguild(ctx: commands.Context):
    if ctx.author.id != ownerId:
        return

    await ctx.send("Synced all commands to *this guild*!")
    await bot.tree.sync(guild=testGuild)


@bot.command()
async def sync(ctx: commands.Context):
    if ctx.author.id != ownerId:
        return

    await ctx.send("Synced all commands *globally*!")
    await bot.tree.sync()


async def main():
    await load_extensions()
    await bot.start(token=BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
