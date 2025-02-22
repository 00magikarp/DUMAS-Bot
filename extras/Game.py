import re
import time
import random

import discord
import pydealer


class Game:
    game_count: int = 0

    CARD_VALUE_SHORTHAND_TO_FORMAL = {
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "10": "10",
        "J": "Jack",
        "Q": "Queen",
        "K": "King",
        "A": "Ace"
    }

    def __init__(self, creator: discord.User):
        self.players: list[discord.User] = []
        self.players.append(creator)
        self.hands: list[pydealer.Stack] = []
        self.started: bool = False
        self.time_started: float = time.time()
        self.current_turn: int = 0
        self.game_id: int = Game.game_count
        self.deck: pydealer.Deck = pydealer.Deck()
        self.deck.shuffle()
        self.card: pydealer.Card | None = None
        self.isCompleted: bool = False
        self.winner: discord.User | None = None

        Game.game_count += 1

    def creator(self) -> discord.User:
        return self.players[0]

    def add_player(self, new: discord.User) -> None:
        self.players.append(new)

    def start(self) -> None:
        self.started = True
        t = self.deck.deal(1)
        self.card = t.get(0)[0]
        for i in range(len(self.players)):
            self.hands.append(self.deck.deal(6))

    def play(self, move: str) -> bool:
        """
        Evaluate a played move.

        :param move: Move string
        :return: If the move was successful.
        """
        output = eval(move.replace("J", "11").replace("Q", "12").replace("K", "13").replace("A", "14"))
        middleValue: int = pydealer.const.VALUES.index(self.card.value) + 2
        if len(move) == 1 and output in (middleValue - 1, middleValue + 1) or output == middleValue:
            move_parsed: list[str] = re.split(r"[+\-]", move)
            lastCardFound: pydealer.Card | None = None
            for input_card in move_parsed:

                lastCardFound = self.hands[self.get_current_turn()][
                    self.hands[self.get_current_turn()].find(input_card)[0]
                ]

                self.hands[self.get_current_turn()].__delitem__(
                    self.hands[self.get_current_turn()].find(input_card)[0]
                )

            self.card = pydealer.Card(lastCardFound.value, lastCardFound.suit)
            self.current_turn += 1
            if not self.hands[self.get_current_turn()]:
                self.isCompleted = True
                self.winner = self.players[self.get_current_turn()]
            return True
        else:
            return False

    def draw(self) -> None:
        self.hands[self.get_current_turn()] += self.deck.deal(1)
        self.current_turn += 1

    def hand(self, user: discord.User) -> str:
        return ", ".join([str(card) for card in self.hands[self.players.index(user)]])

    def get_current_player(self) -> discord.User:
        return self.players[self.get_current_turn()]

    def get_current_turn(self) -> int:
        return self.current_turn % len(self.players)

    def __len__(self) -> int:
        return len(self.players)

    def __str__(self) -> str:
        return f"""\
**Game {self.game_id}:**
> Created by <@{self.creator().id}>
> Started: {"**Yes**" if self.started else "**No**"}"""

    def __repr__(self):
        return f"Game(id={self.game_id},creator=<@{self.creator().id}>,players={self.players},started={self.started})"


