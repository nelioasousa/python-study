"""Blackjack game for command line console/terminal.

Play Blackjack against a Dealer bot. All tradicional decisions are 
available: hit, stand, double, split, and surrender. But not all are 
available as default. The rules/configurations of the game can be 
modified by setting values in the cfg.json file.

CONFIGURABLE RULES:
start_money `int` -- Set the player's bankroll, that is, the value
available to gambling when the game starts. Default is $500 and max
value is $1000.

num_decks `int` -- Number of card decks used to form the draw pile from
which the dealer should draw cards. The default value is 1, and it can
be at a maximum of 6.

max_num_hands `int` -- Maximum number of hands a player can have. This
parameter restrict the number of 'split' decisions a player can make.
The default value is 1, and it can be at a maximum of 6.

hit_soft_17 `bool` -- Dealer must hit when his hand is a soft 17. Set
to True by default.

double_after_splits `bool` -- Allows the 'double' decision after a
'split' decision is made. Set do False by default.

restrict_double `bool` -- The 'double' decision can only be made in
hands with a value of 9, 10, or 11. Set do True by default.

enable_split_in_aces `bool` -- Enable the 'split' decision for hands
with two ace cards. Set do False by default.

enable_surrender `bool` -- Enable the 'surrender' decision. Set do
False by default.

enable_hole_card `bool` -- Enable the hole card, that is, conceal the
second card of the Dealer's hand from the Player. Set do True by
default.

FIXED RULES:
- The 'split' decision places the same bet in the new hand;
- The 'surrender' decision returns the largest integer that is lower
than or equal to half of the bet on the hand (pays ~50%);
- The Dealer only make his moves (hit or stand) at the end of the
round (after the Player end his turn);
- The Dealer must hit until a minumum of 17;
- The Dealer pays double the bets in winning hands (pays 100%);
- Cannot surrender or double bets in hands with a total of 21. Those
hands are automatically closed since no other decision is available;

Intended to be used as a script. Do not take command line arguments.
Script uses pattern matching, available only with Python >= 3.10.
"""

from __future__ import annotations
from collections import namedtuple
from typing import Union, Literal
from random import sample
from collections import Counter
from itertools import product


# See https://stackoverflow.com/q/51671699/16969525
Card = namedtuple('Card', ['rank', 'suit'])


class DrawPile():
    """A class representing a draw pile of cards in a card game.
    
    ATTRIBUTES:

    num_decks `int` -- Number of card decks that form de pile.

    pile `dict[Card, int]` -- Dictionary representing the draw pile.
    Keys are instances of `namedtuple('Card', ['rank', 'suit'])`
    representing all the 52 cards in a conventional deck, while the
    corresponding values are the quantity available within the pile.

    METHODS:

    `draw(num_cards: int) -> List[Card]` -- Draw `num_cards` cards
    randomly from the pile, returning them in a list.
    
    `recompose()` -- Restore the cards withdraw from the pile.
    """

    _ranks = (
        'A', '2', '3',
        '4', '5', '6',
        '7', '8', '9',
        '10', 'J', 'Q', 'K',
        )
    _suits = ('♥', '♦', '♣', '♠')

    def __init__(self, num_decks: int):
        """DrawPile() class initializer.
        
        PARAMETERS:

        num_decks `int` -- Number of decks to form the pile.
        """
        self.num_decks = num_decks
        self.pile = {card: num_decks for card in self._deck()}
    
    def draw(self, num_cards: int = 1) -> list[Card]:
        """Draw `num_cards` cards randomly from the pile.
        
        PARAMETERS:

        num_cards `int` -- Number of cards to draw from the pile.

        RETURN VALUE:

        `list[Card]` -- Cards withdrawn from the pile.
        """
        cards = sample(population=list(self.pile),
                       counts=list(self.pile.values()),
                       k=max(num_cards, 1))
        for card, count in Counter(cards).items():
            self.pile[card] -= count
        return cards

    def recompose(self):
        """Restore the cards withdraw from the pile."""
        self.pile = {card: self.num_decks for card in self.pile}
    
    def _deck(self):
        return [Card(r, s) for r, s in product(self._ranks, self._suits)]


class Hand():
    """A class representing a hand in a Blackjack game.
    
    ATTRIBUTES:

    cards `list[Card]` -- Cards that compose the hand.

    bet `int` -- Value of the wager placed in the hand.

    closed `bool` -- Whether the hand is closed or not, that is, a hand
    that the player cannot or doesn't want to make any more moves. This
    parameter doesn't influence the behavior of the `Hand()` instance.
    Its main purpose is to function as a flag for outside code.

    surrendered `bool` -- Wheter the hand is surrendered or not. This
    parameter doesn't influence the behavior of the `Hand()` instance.
    Its main purpose is to function as a flag for outside code. This
    parameter is set using the `.surrender()` method, as outside code
    must determine whether the `Hand()` instance has been surrendered
    or not.

    busted `bool` -- Whether the hand is busted or not, that is,
    whether the hand has a value above 21. This parameter doesn't
    influence the behavior of the `Hand()` instance. Its main purpose
    is to function as a flag for outside code.

    blackjack `bool` -- Whether the hand is a blackjack or not. This
    parameter doesn't influence the behavior of the `Hand()` instance.
    Its main purpose is to function as a flag for outside code. This
    parameter is set using the `.set_as_blackjack()` method, as outside
    code must determine whether the `Hand()` instance is a blackjack.

    twentyone `bool` -- Whether the hand is a Twenty-One or not, that
    is, whether the hand has a value of exactly 21. This parameter does
    not influence the behavior of the `Hand()` instance. Its main
    purpose is to function as a flag for outside code.

    ranks `list[Literal['A', '2', '3', '4', '5', '6', '7', '8', '9',
    '10', 'J', 'Q', 'K']]` -- The rank of the cards in `.cards`
    attribute.

    METHODS:

    `add_card(card: Card)` -- Add one Card instance to the hand.

    `double()` -- Double bet on the hand.

    `split(bet: int) -> Hand` -- Split the instance in two hands,
    returning the new `Hand()` instance created. `bet` is associated
    with the created hand during its initialization.

    `min_total() -> int` -- Return the lower value of the hand.

    `max_total() -> int` -- Return the higher value of the hand.

    `best_value() -> int` -- Return `.max_value()` if it's less than or
    equal to 21, otherwise, return `.min_value()`.

    `close()` -- Set `.closed` attribute to True.

    `surrender()` -- Set `.surrendered` attribute to True.

    `set_as_blackjack()` -- Set `.blackjack` attribute to True.
    """

    def __init__(self, cards: list[Card], bet: int):
        """Hand() class initializer.
        
        PARAMETERS:
        
        cards `list[Card]` -- Hand initial cards.

        bet `int` -- Wager placed on the hand.
        """
        self.cards = cards
        self.bet = bet
        self.closed = False
        self.surrendered = False
        self.busted = False
        self.blackjack = False
        self.twentyone = False
        self._check_hand()

    def _check_hand(self):
        if self.best_value() == 21:
            self.twentyone = True
            self.closed = True
        elif self.min_total() > 21:
            self.busted = True
            self.closed = True
    
    @property
    def ranks(self) -> list[
            Literal['A', '2', '3',
                    '4', '5', '6',
                    '7', '8', '9',
                    '10', 'J', 'Q', 'K']
            ]:
        return [card.rank for card in self.cards]
    
    def add_card(self, card: Card):
        """Add one Card instance to the hand.
        
        PARAMETERS:
        
        card `Card` -- Card to be added.
        """
        self.cards.append(card)
        self._check_hand()

    def double(self):
        "Double bet on the hand."
        self.bet *= 2

    def split(self, bet: int) -> Hand:
        """Split hand in two.
        
        The new `Hand()` instance is initialized with the `cards`
        parameter being the original hand's last card and with `bet`
        parameter being the value of `bet` passed to the `.split()`
        method.

        PARAMETERS:

        bet `int` -- Wager value to be associated with the new `Hand()`
        instance created.

        RETURN VALUE:

        `Hand` -- Hand created from the spliting of the original hand.
        """
        other_hand = self.cards[-1:]
        self.cards = self.cards[:-1]
        return Hand(cards=other_hand, bet=bet)
    
    def min_total(self) -> int:
        """Calculate the lower value of the hand.
        
        All ace cards are treated as being of value 1.

        RETURN VALUE:

        `int` -- Lower value of the hand.
        """
        return sum(1 if r == 'A' \
                   else 10 if r in {'J', 'Q', 'K'} \
                   else int(r) for r in self.ranks)
    
    def max_total(self) -> int:
        """Calculate the higher value of the hand.
        
        At most one ace card assumes a value of 11 and the remaining
        aces are treated as being of value 1.

        RETURN VALUE:

        `int` -- Higher value of the hand.
        """
        if 'A' in self.ranks:
            return self.min_total() + 10
        return self.min_total()
    
    def best_value(self) -> int:
        """Calculate the best value of the hand.
        
        The best value is considered the higher value of the hand when
        its lower than or equal to 21. Whem the higher value is greatar
        than 21, the best value is the lower value.

        RETURN VALUE:

        `int` -- Best value of the hand.
        """
        hand_max = self.max_total()
        if hand_max <= 21:
            return hand_max
        return self.min_total()

    def close(self):
        """Set hand as closed."""
        self.closed = True
    
    def surrender(self):
        """Set hand as surrendered."""
        self.closed = True
        self.surrendered = True
    
    def set_as_blackjack(self):
        """Set hand as a blackjack."""
        self.blackjack = True


def play(start_money: int = 500,
         num_decks: int = 1,
         max_num_hands: int = 1,
         hit_soft_17: bool = False,
         double_after_splits: bool = False,
         restrict_double: bool = False,
         enable_split_in_aces: bool = False,
         enable_surrender: bool = False,
         enable_hole_card: bool = False):
    """Handle the blackjack game logic.
    
    PARAMETERS:

    start_money `int` -- Player bankroll.

    num_decks `int` -- Number of card decks to form the draw pile.

    max_num_hands `int` -- Maximum number of hands a Player can have.
    This parameter limits the number of 'split' decisions a Player can
    make.

    hit_soft_17 `bool` -- Dealer must hit when they hand is a soft 17.

    double_after_splits `bool` -- Player can 'double' after have
    decided to 'split'.

    restrict_double `bool` -- Player can 'double' bets only in hands
    with a lower value of 9, 10, or 11.

    enable_split_in_aces `bool` -- Player can 'split' hands with two
    ace cards.

    enable_surrender `bool` -- Decision 'surrender' is available for
    the Player. But it is only allowed in not busted hands that are not
    twenty-one.

    enable_hole_card `bool` -- The Dealer's second card is concealed
    from the Player until their turn ends.
    """
    bankroll = start_money
    pile = DrawPile(num_decks)
    while bankroll:
        message = "Let's start! Place your bet."
        while True:
            table_screen(bankroll=bankroll, message=message)
            bet = ask_bet()
            if bet is None or bet < 1:
                message = 'You must enter a positive integer number.'
            elif bet > bankroll:
                message = 'You do not have enough funds.'
            else:
                bankroll -= bet
                message = None
                break
        dealer_hand = Hand(cards=pile.draw(2), bet=0)
        player_hands = [Hand(cards=pile.draw(2), bet=bet)]
        if dealer_hand.twentyone:
            dealer_hand.set_as_blackjack()
        if player_hands[0].twentyone:
            player_hands[0].set_as_blackjack()
        num_split = max_num_hands - 1
        while sum(not h.closed for h in player_hands):
            temp_bankroll = bankroll
            decisions = [None] * len(player_hands)
            for i, hand in enumerate(player_hands, start=1):
                if hand.closed: continue
                message = 'Make a decision for HAND %d.\n' \
                          'Hit, stand, double, split, or surrender?'%i
                while True:
                    table_screen(dealer_hand=dealer_hand,
                                 hole_card=enable_hole_card,
                                 player_hands=player_hands,
                                 decisions=decisions,
                                 bankroll=bankroll,
                                 message=message)
                    decision = input('Your decision for HAND %d: '%i)
                    if decision in {'hit', 'stand'}:
                        pass
                    elif decision == 'split':
                        if not num_split:
                            message = 'Cannot split HAND %d. ' \
                                      'Max number of hands reached.'%i
                            continue
                        if not enable_split_in_aces \
                                and hand.ranks == ['A', 'A']:
                            message = 'Cannot split HAND %d. ' \
                                      'Split aces is not allowed.'%i
                            continue
                        if len(hand.cards) != 2 or len(set(hand.ranks)) != 1:
                            message = 'Cannot split HAND %d.'%i
                            continue
                        if hand.bet > temp_bankroll:
                            message = 'Cannot split HAND %d. ' \
                                      'You do not have enough funds.'%i
                            continue
                        temp_bankroll -= hand.bet
                    elif decision == 'double':
                        if len(player_hands) > 1 and not double_after_splits:
                            message = 'Cannot double HAND %d. ' \
                                      'Double after split is not allowed.'%i
                            continue
                        if restrict_double \
                                and hand.min_total() not in {9, 10, 11}:
                            message = 'Cannot double HAND %d. ' \
                                      'Double only allowed on 9, 10, or 11.'%i
                            continue
                        if hand.bet > temp_bankroll:
                            message = 'Cannot double HAND %d. ' \
                                      'You do not have enough funds.'%i
                            continue
                        temp_bankroll -= hand.bet
                    elif decision == 'surrender':
                        if not enable_surrender:
                            message = 'Invalid decision for HAND %d. ' \
                                      'Surrender is not allowed.'%i
                            continue
                        pass
                    else:
                        message = 'Not understood. ' \
                                  'Waiting decision for HAND %d.\n' \
                                  'Hit, stand, double, split, or surrender?'%i
                        continue
                    message = None
                    decisions[i-1] = decision
                    break
            cost = process_decisions(player_hands, decisions, pile)
            bankroll -= cost
        dealer_play(dealer_hand, hit_soft_17, pile)
        results = get_results(dealer_hand, player_hands)
        bankroll += sum(r[1] for r in results)
        pile.recompose()
        table_screen(dealer_hand=dealer_hand,
                     player_hands=player_hands,
                     bankroll=bankroll,
                     message='Round is over. Here the results.',
                     results=results)
        enter_to_continue()
    return end_of_game()

def table_screen(bankroll: int,
                 dealer_hand: Union[Hand, None] = None,
                 hole_card: bool = True,
                 player_hands: Union[list[Hand], None] = None,
                 decisions: Union[list[str], None] = None,
                 message: Union[str, None] = None,
                 results: Union[list[tuple[str, int]], None] = None):
    """Handle the game screen printing."""
    clear_terminal()
    if dealer_hand is None:
        print('DEALER: ? ?', end='\n\n')
    elif results is not None:
        cards_repr = ' '.join(card_repr(c) for c in dealer_hand.cards)
        hand_result = 'Blackjack' if dealer_hand.blackjack \
            else 'Twenty-One' if dealer_hand.twentyone \
            else str(dealer_hand.best_value())
        print('DEALER: %s (%s)' %(cards_repr, hand_result), end='\n\n')
    elif hole_card:
        print('DEALER: %s ?' %card_repr(dealer_hand.cards[0]), end='\n\n')
    else:
        print('DEALER: %s'
            %' '.join(card_repr(c) for c in dealer_hand.cards), end='\n\n')
    if message is not None:
        print('[!] %s' %message, end='\n\n')
    print('PLAYER ($%d)' %bankroll, end='\n\n')
    if player_hands is None:
        print('(Waiting bet) H1: ? ?', end='\n\n')
    else:
        for i, hand in enumerate(player_hands):
            status = 'Surrendered' if hand.surrendered \
                else 'Blackjack' if hand.blackjack \
                else 'Twenty-One' if hand.twentyone \
                else 'Busted' if hand.busted \
                else 'Closed' if hand.closed \
                else 'Open'
            cards_repr = ' '.join(card_repr(c) for c in hand.cards)
            if decisions:
                decision = decisions[i]
                suffix = '' if decision is None else '(%s)' %decision
            elif results:
                suffix = '[{} / +${}]'.format(*results[i])
            else:
                suffix = ''
            print('(%s) $%d in H%d: %s %s' 
                  %(status, hand.bet, i+1, cards_repr, suffix))
        print('')

def card_repr(card: Card) -> str:
    """Return the string representation of `card`."""
    return '%s%s' %(card.rank, card.suit)

def ask_bet() -> Union[int, None]:
    """Ask the value of the initial bet to the Player."""
    response = input('Initial bet: $')
    try:
        return int(response)
    except ValueError:
        return None

def process_decisions(
        hands: list[Hand],
        decisions: list[
            Literal['hit', 'stand', 'double', 'split', 'surrender']
            ],
        pile: DrawPile) -> int:
    """Process the `hands` according to the player's `decisions`."""
    cost = 0
    while 'split' in decisions:
        index = decisions.index('split')
        hand = hands[index]
        cost += hand.bet
        new_hand = hand.split(hand.bet)
        hands.insert(index + 1, new_hand)
        decisions[index : index+1] = ['hit', 'hit']
    for i, decision in enumerate(decisions):
        hand = hands[i]
        match decision:
            case 'hit':
                hand.add_card(pile.draw()[0])
            case 'stand':
                hand.close()
            case 'double':
                cost += hand.bet
                hand.double()
            case 'surrender':
                hand.surrender()
    return cost

def dealer_play(hand: Hand, hit_soft_17: bool, pile: DrawPile):
    """Run the Dealer game logic."""
    if sorted(hand.ranks) == ['6', 'A']:
        if hit_soft_17:
            hand.add_card(pile.draw()[0])
        return
    while hand.min_total() < 17 and not hand.closed:
        hand.add_card(pile.draw()[0])

def get_results(
        dealer_hand: Hand, player_hands: list[Hand]
        ) -> list[tuple[Literal['win', 'lost', 'draw', 'surrendered'], int]]:
    """Compare the `player_hands` against the `dealer_hand`.

    For each hand in `player_hands`, compare against `dealer_hand` and
    determine whether the hand wins, loses, draws, or surrenders, along
    with the corresponding value that must be returned to the Player,
    if any.
    """
    results = []
    dealer_best = dealer_hand.best_value()
    for hand in player_hands:
        if hand.surrendered:
            results.append(('surrendered', hand.bet // 2))
        elif hand.busted:
            results.append(('lost', 0))
        elif dealer_hand.busted:
            results.append(('win', hand.bet * 2))
        else:
            hand_best = hand.best_value()
            if hand_best == dealer_best:
                results.append(('draw', hand.bet))
            elif hand_best > dealer_best:
                results.append(('win', hand.bet * 2))
            else:
                results.append(('lost', 0))
    return results

def enter_to_continue():
    """Ask the user to press Enter before continuing."""
    input('Press Enter to continue...')
    return

def end_of_game():
    """End of game screen."""
    clear_terminal()
    print('Sheesh! You lost all your money...')
    enter_to_continue()
    return

def terminate():
    """Script exit screen."""
    clear_terminal()
    print('Tranks for playing! Goodbye!')
    print('More in github.com/nelioasousa/python-study')

def clear_terminal():
    """Clear the terminal."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def menu(info: Union[str, None] = None) -> str:
    """Handle the menu screen."""
    clear_terminal()
    print('♣♥♠♦ BLACKJACK GAME ♣♥♠♦', end='\n\n')
    print('[P] PLAY\n[E] EXIT', end='\n\n')
    return input('Select: ').strip().lower()


def load_configs() -> dict[str, Union[bool, int]]:
    """Load the game configurations file.
    
    RETURN VALUE:

    `dict[str, Union[bool, int]]` -- Configurations as a dictionary,
    where keys are the parameters names and values are the parameters
    values.

    EXCEPTIONS RAISED:

    `AssertionError` -- Raised when there are missing or unknown
    parameters in the cfg.json file. An `AssertionError` is also raised
    when the parameter values are not of the expected type or fall
    outside the allowed range.
    """
    from json import load
    try:
        with open('./cfg.json', mode='br') as cfg_file:
            cfg_dict = load(cfg_file)
            assert isinstance(cfg_dict, dict), \
                "Couldn't understand the cfg.json file"
    except FileNotFoundError:
        return reset_configs()
    default_cfg = get_default_configs()
    dft_params = frozenset(default_cfg)
    cfg_params = frozenset(cfg_dict)
    missing = dft_params - cfg_params
    extra = cfg_params - dft_params
    if missing or extra:
        error_message = 'Missing and/or unknown parameters in cfg.json'
        if missing:
            error_message += '\n    - Missing: %s' \
                %', '.join('"%s"' %m for m in missing)
        if extra:
            error_message += '\n    - Unknown: %s' \
                %', '.join('"%s"' %e for e in extra)
        raise AssertionError(error_message)
    max_values = {"start_money": 1000, "num_decks": 6, "max_num_hands": 6}
    for param, value in cfg_dict.items():
        dft_value = default_cfg[param]
        assert isinstance(value, type(dft_value)), \
            "Parameter '%s' must have a value of type '%s': " \
            "got '%s' of type '%s' instead" %(param,
                                              type(dft_value).__name__,
                                              value,
                                              type(value).__name__)
        try:
            max_value = max_values[param]
            assert 0 < value <= max_value, \
                "Parameter '%s' must have a value greater than 0 and " \
                "at most %d: got %d instead" %(param, max_value, value)
        except KeyError:
            continue
    return cfg_dict

def reset_configs() -> dict[str, Union[bool, int]]:
    """Reset the configurations file to the default configuration."""
    configs = get_default_configs()
    save_configs(configs)
    return configs

def get_default_configs() -> dict[str, Union[bool, int]]:
    """Get default configurations dictionary."""
    return {"start_money": 500,
            "num_decks": 1,
            "max_num_hands": 1,
            "hit_soft_17": True,
            "double_after_splits": False,
            "split_in_aces": False,
            "restrict_double": True,
            "enable_surrender": False,
            "enable_hole_card": True}

def save_configs(configs: dict[str, Union[bool, int]]):
    """Save `configs` to `./cfg.json` file."""
    from json import dump
    with open('./cfg.json', mode='w') as cfg_file:
        dump(configs, cfg_file, ensure_ascii=True, indent=4)

def handle_configs_error(
        error_message: str
        ) -> Union[dict[str, Union[bool, int]], None]:
    """Handle configurations files out of order."""
    clear_terminal()
    while True:
        print('An error occured while reading the configurations:\n')
        print(error_message, end='\n\n')
        response = input('Reset configuration file? [y]es or [n]o ')
        match response.strip().lower():
            case 'yes' | 'y':
                return reset_configs()
            case 'no' | 'n':
                return None


def main():
    try:
        configs = load_configs()
    except AssertionError as e:
        configs = handle_configs_error(e.args[0])
        if configs is None: raise e
    while True:
        match menu():
            case 'play' | 'p':
                play(**configs)
            case 'exit' | 'e':
                return terminate()
            case _:
                continue


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        terminate()
