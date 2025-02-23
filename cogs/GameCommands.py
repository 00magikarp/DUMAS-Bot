import re

import discord
from discord.ext import commands

from extras.Game import Game


# noinspection PyUnresolvedReferences
class GameCommands(commands.GroupCog, name="game", description="Game commands"):
    games: dict[discord.TextChannel, Game] = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="create",
        description="Create a new DUMAS Game"
    )
    async def create(self, interaction: discord.Interaction) -> None:
        """
        Create a new DUMAS Game

        :param interaction: The interaction object.
        """
        if interaction.channel in GameCommands.games.keys():
            await interaction.response.send_message("Game already exists in this channel.")
            return

        GameCommands.games[interaction.channel] = Game(interaction.user, interaction.channel)
        await interaction.response.send_message(
            f"Created new game by <@{interaction.user.id}> Will be auto-aborted in 5 minutes."
        )
        await interaction.defer()

        asyncio.sleep(60 * 5)
        if not GameCommands.games[interaction.channel].started:
            await interaction.followup.send("Game auto-aborted after 5 minutes.")
            del GameCommands.games[interaction.channel]

    @discord.app_commands.command(
        name="join",
        description="Join a DUMAS game"
    )
    async def join(self, interaction: discord.Interaction) -> None:
        """
        Join a DUMAS game. Must be created in same channel

        :param interaction: The interaction object.
        """
        if interaction.channel not in GameCommands.games.keys():
            await interaction.response.send_message("Game doesn't exist in channel yet! Run `/game create` to make one.")
        if interaction.user in GameCommands.games[interaction.channel].players:
            await interaction.response.send_message("You're already in this game!")
            return
        if GameCommands.games[interaction.channel].started:
            await interaction.response.send_message("**ERROR**: Game already exists and is started.")
            return
        if len(GameCommands.games[interaction.channel].players) >= 5:
            await interaction.response.send_message("Sorry, too many players have joined already!")
            return
        GameCommands.games[interaction.channel].players.append(interaction.user)

        await interaction.response.send_message(
            f"<@{interaction.user.id}> has joined game in <#{interaction.channel.id}>!"
        )

    @discord.app_commands.command(
        name="abort",
        description="Abort a game you created before it starts"
    )
    async def abort(self, interaction: discord.Interaction) -> None:
        """
        Abort a game you created before it starts

        :param interaction: The interaction object.
        """
        if GameCommands.games[interaction.channel].creator() != interaction.user:
            await interaction.response.send_message("**ERROR**: You are not the user who created the game")
            return
        if GameCommands.games[interaction.channel].started:
            await interaction.response.send_message("Cannot abort a started game.")
            return

        await interaction.response.send_message(
            f"Game in <#{interaction.channel.id}> has been aborted by <@{interaction.user.id}>"
        )
        del GameCommands.games[interaction.channel]

    @discord.app_commands.command(
        name="viewall",
        description="View all created games"
    )
    async def viewall(self, interaction: discord.Interaction) -> None:
        """
        View all created games

        :param interaction: The interaction object.
        """
        if not GameCommands.games:
            await interaction.response.send_message("No games created yet! Create one with `/game create`")
            return

        output: str = "### All games\n"
        for game in GameCommands.games.values():
            output += str(game) + "\n"
        await interaction.response.send_message(output)

    @discord.app_commands.command(
        name="debugview",
        description="View data of all created games"
    )
    async def debugview(self, interaction: discord.Interaction) -> None:
        """
        View data of all created games

        :param interaction: The interaction object.
        """
        if not GameCommands.games:
            await interaction.response.send_message("No games created yet! Create one with `/game create`")
            return

        output: str = "### All games\n"
        for game in GameCommands.games.values():
            output += repr(game) + "\n"
        await interaction.response.send_message(output)

    @discord.app_commands.command(
        name="hand",
        description="View your current hand"
    )
    async def hand(self, interaction: discord.Interaction) -> None:
        """
        View your current hand

        :param interaction: The interaction object.
        """
        if interaction.channel not in GameCommands.games.keys():
            await interaction.response.send_message("Game doesn't exist.", ephemeral=True)
            return
        if interaction.user not in GameCommands.games[interaction.channel].players:
            await interaction.response.send_message("You're not in that game!", ephemeral=True)
            return
        if not GameCommands.games[interaction.channel].started:
            await interaction.response.send_message("Game hasn't started yet!", ephemeral=True)
            return

        await interaction.response.send_message(
            GameCommands.games[interaction.channel].hand(interaction.user),
            ephemeral=True
        )

    @discord.app_commands.command(
        name="start",
        description="Start the game you created"
    )
    async def start(self, interaction: discord.Interaction) -> None:
        """
        Start the game you created

        :param interaction: The interaction object.
        """
        if interaction.channel not in GameCommands.games.keys():
            await interaction.response.send_message("Game does not exist!")
            return
        if interaction.user != GameCommands.games[interaction.channel].creator():
            await interaction.response.send_message("Cannot start a game you haven't created!")
            return

        GameCommands.games[interaction.channel].start()

        await interaction.response.send_message(f"{GameCommands.games[interaction.channel].get_current_card()}")
        await interaction.followup.send(f"<@{GameCommands.games[interaction.channel].get_current_player().id}>'s turn!")

    @discord.app_commands.command(
        name="play",
        description="Play your turn"
    )
    async def play(self, interaction: discord.Interaction, move: str) -> None:
        """
        Play your turn

        :param interaction: The interaction object.
        :param move: Your play for the turn. '/game play draw' to draw a card.
        """
        if interaction.channel not in GameCommands.games.keys():
            await interaction.response.send_message("Game does not exist!")
            return
        if interaction.user not in GameCommands.games[interaction.channel].players:
            await interaction.response.send_message("You're not in this game!", ephemeral=True)
            return
        if not GameCommands.games[interaction.channel].started:
            await interaction.response.send_message("Game hasn't started yet!", ephemeral=True)
            return
        if GameCommands.games[interaction.channel].get_current_player() != interaction.user:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        if move.lower() == "draw":
            GameCommands.games[interaction.channel].draw()
            await interaction.response.send_message(f"{GameCommands.games[interaction.channel].get_current_card()}")
            await interaction.followup.send(f"<@{GameCommands.games[interaction.channel].get_current_player().id}>'s turn!")
            return

        cards_with_operations = re.findall(r"[a-zA-Z]+|\d+|[+\-]", move)

        if len(cards_with_operations) % 2 != 1:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> Invalid move! (err: incorrect ratio of terms to operators)"
            )
            return

        for char in move:
            if not (char.isnumeric() or char in ['A', 'J', 'Q', 'K', '+', '-']):
                await interaction.response.send_message(
                    f"<@{interaction.user.id}> Invalid move! (err: illegal character)"
                )
                return

        current_char_is_numeric = True

        for char in cards_with_operations:
            if current_char_is_numeric ^ (char.isnumeric() or char.upper() in ['J', 'Q', 'K', 'A']):
                await interaction.response.send_message(
                    f"<@{interaction.user.id}> Invalid move! (err: illegal sequence of characters)"
                )
                return
            current_char_is_numeric = not current_char_is_numeric

        move_parsed: list[str] = re.split(r"[+\-]", move)
        current_hand: list[str] = [
            str(card.value.replace("Jack", "J").replace("Queen", "Q").replace("King", "K").replace("Ace", "A"))
            for card in GameCommands.games[interaction.channel].hands[
                GameCommands.games[interaction.channel].get_current_turn()
            ]
        ]

        for char in move_parsed:
            if (char.upper() not in ['2', '3', '4', '5', '6', '7', '8', '9', '10',
                                     'A', 'J', 'Q', 'K'] or
                    char not in current_hand):
                await interaction.response.send_message(
                    f"<@{interaction.user.id}> Invalid move! (err: illegal term)"
                )
                return
            current_hand.remove(char.upper())

        if GameCommands.games[interaction.channel].isCompleted:
            await interaction.followup.send(
                f"Game has completed! Winner is **<@{GameCommands.games[interaction.channel].winner.id}>!"
            )
            del GameCommands.games[interaction.channel]
            return

        if GameCommands.games[interaction.channel].play(move):
            await interaction.response.send_message(f"{GameCommands.games[interaction.channel].get_current_card()}")
            await interaction.followup.send(f"<@{GameCommands.games[interaction.channel].get_current_player().id}>'s turn!")
        else:
            await interaction.response.send_message(f"<@{interaction.user.id}> Invalid move! (err: rejected)")


async def setup(bot):
    await bot.add_cog(GameCommands(bot))
