
"""Module for simulating blackjack.
   Games are played with infinite deck
   Player acts according to the csv files
   Dealer can be set to either hit or stand on soft 17
   Source to csv files https://wizardofodds.com/games/blackjack/expected-return-infinite-deck/"""

import csv
import time
import pandas
from random import choice
import matplotlib.pyplot as plo


strategy_hard_hands = "strategy/optimal_strategy_hard.csv"
strategy_soft_hands = "strategy/optimal_strategy_soft.csv"
strategy_hard_hands_17 = "strategy_hit_soft17/optimal_strategy_hard.csv"
strategy_soft_hands_17 = "strategy_hit_soft17/optimal_strategy_soft.csv"


def from_csv_to_dict(file):
    # reads csv files to nested dicts
    # player's hand value and dealer's card as keys and optimal responses as values

    with open(file, "r") as csv_file:
        reader = csv.reader(csv_file, delimiter="\t")
        dealer_cards = next(reader)
        del dealer_cards[0]  # deleting the value on the top left corner
        hand_values = []
        data = []

        for line in reader:
            hand_values.append(line.pop(0))
            data.append(line)

    inner_dicts = []

    for row in data:
        inner_dicts.append(dict(zip(dealer_cards, row)))

    nested_dict = dict(zip(hand_values, inner_dicts))

    return nested_dict


strategy_dict_hard = from_csv_to_dict(strategy_hard_hands)
strategy_dict_soft = from_csv_to_dict(strategy_soft_hands)
strategy_dict_hard_17 = from_csv_to_dict(strategy_hard_hands_17)
strategy_dict_soft_17 = from_csv_to_dict(strategy_soft_hands_17)


CARD_DECK = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9"] + 4 * ["10"]


def draw_card(hand):
    hand.append(choice(CARD_DECK))


hand_value_cache = {}


def hand_value(hand):

    try:
        value = hand_value_cache[tuple(hand)]
    except KeyError:
        if "Ace" not in hand:
            value = sum(list(map(int, hand)))
        else:
            aces = hand.count("Ace")
            no_ace_hand = [card for card in hand if card != "Ace"]

            value = sum(list(map(int, no_ace_hand)))

            for ace in range(aces):
                if value <= 10:
                    value += 11
                else:
                    value += 1

        hand_value_cache[tuple(hand)] = value

    return value


def soft_hand(hand):
    # notice that hand isn't soft even if it contains aces
    # if the aces can only have the value of one without player busting
    if "Ace" in hand and sum(map(int, [card for card in hand if card != "Ace"])) <= 10:
        is_soft = True
    else:
        is_soft = False
    return is_soft


def players_response(option, hand, bet):

    surrendered = False
    stand = False
    blackjack = False
    double = False
    if option == "R":
        surrendered = True
        bet = bet / 2
    elif option == "S":
        stand = True
        if hand_value(hand) == 21 and len(hand) == 2:
            blackjack = True
            bet *= 1.5
    else:
        if option == "D" and len(hand) == 2:
            # after doubling player gets only one additional card
            double = True
            bet *= 2

    return bet, surrendered, stand, blackjack, double


def dealers_response(hand, hits_soft_17=False):
    bust = False

    if not hits_soft_17:
        while hand_value(hand) <= 16:
            draw_card(hand)
    else:
        while True:
            value = hand_value(hand)
            soft = soft_hand(hand)

            if not soft and value >= 16:
                break
            elif soft and value >= 17:
                break
            else:
                draw_card(hand)

    if hand_value(hand) > 21:
        bust = True

    return hand, bust


def play_blackjack(bet, soft_17_rule=False):
    """function that plays a round of blackjack according to the optimal strategy and returns the win"""
    bust = False
    stand = False
    surrendered = False

    player_hand = []
    dealer_hand = []
    draw_card(player_hand)
    draw_card(player_hand)
    draw_card(dealer_hand)

    player_hand_value = hand_value(player_hand)

    while not bust and not stand and not surrendered:

        if not soft_17_rule:
            if soft_hand(player_hand):
                optimal_choice = strategy_dict_soft[str(player_hand_value)][dealer_hand[0]]
            else:
                optimal_choice = strategy_dict_hard[str(player_hand_value)][dealer_hand[0]]
        else:
            if soft_hand(player_hand):
                optimal_choice = strategy_dict_soft_17[str(player_hand_value)][dealer_hand[0]]
            else:
                optimal_choice = strategy_dict_hard_17[str(player_hand_value)][dealer_hand[0]]

        response = players_response(optimal_choice, player_hand, bet)
        bet, surrendered, stand, blackjack, double = response

        if not stand and not surrendered:
            draw_card(player_hand)
            if double:
                stand = True

        player_hand_value = hand_value(player_hand)

        if player_hand_value > 21:
            bust = True

    if bust or surrendered:
        # players_response-function automatically cuts the bet in half when surrendering
        win = - bet
    else:
        dealer_hand, dealer_bust = dealers_response(dealer_hand, soft_17_rule)
        dealer_hand_value = hand_value(dealer_hand)

        if player_hand_value > dealer_hand_value or dealer_bust:
            win = bet
        elif player_hand_value < dealer_hand_value:
            win = - bet
        else:
            win = 0

    return win


class Simulation:
    def __init__(self, rounds, bet_value, dealer_hits_soft_17=False):
        self.rounds = rounds
        self.bet_value = bet_value
        self.round_results = []
        self.wins = 0
        self.loses = 0
        self.ties = 0
        self.surrenders = 0
        self.blackjacks = 0
        self.win_amount_total = 0
        self.cumulative_profit = []

        start = time.perf_counter()

        for _ in range(rounds):
            result = play_blackjack(bet_value, dealer_hits_soft_17)
            self.round_results.append(result)
            self.win_amount_total += result
            self.cumulative_profit.append(self.win_amount_total)

            if result == 1.5 * bet_value:
                self.blackjacks += 1
                self.wins += 1
            elif result == bet_value:
                self.wins += 1
            elif result == -0.5 * bet_value:
                self.surrenders += 1
            elif result == 0:
                self.ties += 1
            else:
                self.loses += 1

        finnish = time.perf_counter()

        self.running_time = finnish - start
        self.win_percent = self.win_amount_total / (self.rounds * self.bet_value) * 100

    def overview(self):
        print(f"{self.rounds} rounds of blackjack played according to the optimal strategy "
              f"(infinite deck, no splitting) with bet of {self.bet_value}:\n")
        print("Wins:", self.wins)
        print("Loses:", self.loses)
        print("Ties:", self.ties)
        print("Surrenders:", self.surrenders)
        print("Blackjacks:", self.blackjacks)
        print("")
        print("Win amount:", self.win_amount_total)
        print(f"Win percent: {round(self.win_percent, 2)}%")
        print("")
        print(f"Simulation completed in {self.running_time} seconds")

    def plot_profit_cumulative(self):
        axis = pandas.Series(self.cumulative_profit).plot(title="Profit over time")
        axis.set(ylabel="Cumulative win", xlabel="Round")
        plo.show()

    def plot_profit_percent(self):
        percent_list = []

        for i, value in enumerate(self.cumulative_profit):
            percent_list.append((value / ((i + 1) * self.bet_value)) * 100)

        percent_series = pandas.Series(percent_list)
        axis = percent_series.plot(title="Win percent over time")
        axis.set(ylabel="Win percent", xlabel="Round")
        plo.show()
