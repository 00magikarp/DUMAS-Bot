import re
import time
import random

import discord
import pydealer


class Game:
    CARD_TO_EMOJI = {
        pydealer.Card("2", "Spades"): "<:2s:1343050473166602332>",
        pydealer.Card("3", "Spades"): "<:3s:1343050463699796019>",
        pydealer.Card("4", "Spades"): "<:4s:1343050455516971029>",
        pydealer.Card("5", "Spades"): "<:5s:1343050446968852492>",
        pydealer.Card("6", "Spades"): "<:6s:1343050410499244153>",
        pydealer.Card("7", "Spades"): "<:7s:1343050402769141852>",
        pydealer.Card("8", "Spades"): "<:8s:1343050379159670804>",
        pydealer.Card("9", "Spades"): "<:9s:1343050368107544616>",
        pydealer.Card("10", "Spades"): "<:10s:1343050357563068499>",
        pydealer.Card("Jack", "Spades"): "<:Js:1343050347673030750>",
        pydealer.Card("Queen", "Spades"): "<:Qs:1343050335593304176>",
        pydealer.Card("King", "Spades"): "<:Ks:1343050320174907434>",
        pydealer.Card("Ace", "Spades"): "<:As:1343050308762337330>",

        pydealer.Card("2", "Hearts"): "<:2h:1343050294749040734>",
        pydealer.Card("3", "Hearts"): "<:3h:1343050286079410236>",
        pydealer.Card("4", "Hearts"): "<:4h:1343050276873179206>",
        pydealer.Card("5", "Hearts"): "<:5h:1343050269105193141>",
        pydealer.Card("6", "Hearts"): "<:6h:1343050259215155201>",
        pydealer.Card("7", "Hearts"): "<:7h:1343050239925293188>",
        pydealer.Card("8", "Hearts"): "<:8h:1343050230446424165>",
        pydealer.Card("9", "Hearts"): "<:9h:1343050220518506506>",
        pydealer.Card("10", "Hearts"): "<:10h:1343050207805571224>",
        pydealer.Card("Jack", "Hearts"): "<:Jh:1343050195872514102>",
        pydealer.Card("Queen", "Hearts"): "<:Qh:1343050186519216239>",
        pydealer.Card("King", "Hearts"): "<:Kh:1343050164851445841>",
        pydealer.Card("Ace", "Hearts"): "<:Ah:1343050147185295381>",

        pydealer.Card("2", "Diamonds"): "<:2d:1343050134283489320>",
        pydealer.Card("3", "Diamonds"): "<:3d:1343050121499246642>",
        pydealer.Card("4", "Diamonds"): "<:4d:1343050111428726785>",
        pydealer.Card("5", "Diamonds"): "<:5d:1343050095469395998>",
        pydealer.Card("6", "Diamonds"): "<:6d:1343050082135572562>",
        pydealer.Card("7", "Diamonds"): "<:7d:1343050067963285514>",
        pydealer.Card("8", "Diamonds"): "<:8d:1343050056516763730>",
        pydealer.Card("9", "Diamonds"): "<:9d:1343050043380465775>",
        pydealer.Card("10", "Diamonds"): "<:10d:1343050028968575088>",
        pydealer.Card("Jack", "Diamonds"): "<:Jd:1343049981921202196>",
        pydealer.Card("Queen", "Diamonds"): "<:Qd:1343049971695353926>",
        pydealer.Card("King", "Diamonds"): "<:Kd:1343049957321474120>",
        pydealer.Card("Ace", "Diamonds"): "<:Ad:1343049943602167849>",

        pydealer.Card("2", "Clubs"): "<:2c:1343049928267534416>",
        pydealer.Card("3", "Clubs"): "<:3c:1343049921229492254>",
        pydealer.Card("4", "Clubs"): "<:4c:1343049913340133416>",
        pydealer.Card("5", "Clubs"): "<:5c:1343049904569712651>",
        pydealer.Card("6", "Clubs"): "<:6c:1343049894650314822>",
        pydealer.Card("7", "Clubs"): "<:7c:1343049885880156180>",
        pydealer.Card("8", "Clubs"): "<:8c:1343049873951555616>",
        pydealer.Card("9", "Clubs"): "<:9c:1343049836177657978>",
        pydealer.Card("10", "Clubs"): "<:10c:1343049827193458718>",
        pydealer.Card("Jack", "Clubs"): "<:Jc:1343049810998988862>",
        pydealer.Card("Queen", "Clubs"): "<:Qc:1343049802056863764>",
        pydealer.Card("King", "Clubs"): "<:Kc:1343049791323766916>",
        pydealer.Card("Ace", "Clubs"): "<:Ac:1343049779600429208>",
    }

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

    def __init__(self, creator: discord.User, channel: discord.TextChannel):
        self.players: list[discord.User] = [creator,]
        self.channel: discord.TextChannel = channel
        self.started: bool = False
        self.current_turn: int = 0

        self.deck: pydealer.Deck = pydealer.Deck()
        self.deck.shuffle()
        self.hands: list[pydealer.Stack] = []
        self.card: pydealer.Card | None = None

        self.isCompleted: bool = False
        self.winner: discord.User | None = None

    def creator(self) -> discord.User:
        return self.players[0]

    def add_player(self, new: discord.User) -> None:
        self.players.append(new)

    def start(self) -> None:
        self.started = True
        t = self.deck.deal(1)
        self.card = t.get(0)[0]
        for i in range(len(self.players)):
            self.hands.append(self.deck.deal(8))

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
            if not self.hands[self.get_current_turn()]:
                self.isCompleted = True
                self.winner = self.players[self.get_current_turn()]
            self.current_turn += 1
            return True
        else:
            return False

    def draw(self) -> None:
        self.hands[self.get_current_turn()] += self.deck.deal(1)
        self.current_turn += 1

    def hand(self, user: discord.User) -> str:
        return " ".join([Game.CARD_TO_EMOJI[card] for card in self.hands[self.players.index(user)]])

    def get_current_player(self) -> discord.User:
        return self.players[self.get_current_turn()]

    def get_current_turn(self) -> int:
        return self.current_turn % len(self.players)

    def get_current_card(self) -> str:
        return Game.CARD_TO_EMOJI[self.card]

    def __len__(self) -> int:
        return len(self.players)

    def __str__(self) -> str:
        return f"""\
**Game in <#{self.channel.id}>:**
> Created by <@{self.creator().id}>
> Started: {"**Yes**" if self.started else "**No**"}"""

    def __repr__(self):
        return f"Game(id={self.game_id},creator=<@{self.creator().id}>,players={self.players},started={self.started})"
