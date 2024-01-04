from __future__ import annotations
from collections import namedtuple
from typing import Union, Literal
from random import sample
from collections import Counter
from itertools import product


# See https://stackoverflow.com/q/51671699/16969525
Card = namedtuple('Card', ['rank', 'suit'])


class DrawPile():
    _ranks = (
        'A', '2', '3',
        '4', '5', '6',
        '7', '8', '9',
        '10', 'J', 'Q', 'K',
        )
    _suits = ('♥', '♦', '♣', '♠')

    def __init__(self, num_decks: int):
        self.num_decks = num_decks
        self.pile = {card: num_decks for card in self._deck()}
    
    def draw(self, num_cards: int = 1) -> list[Card]:
        cards = sample(population=list(self.pile),
                       counts=list(self.pile.values()),
                       k=max(num_cards, 1))
        for card, count in Counter(cards).items():
            self.pile[card] -= count
        return cards

    def recompose(self):
        self.pile = {card: self.num_decks for card in self.pile}
    
    def _deck(self):
        return [Card(r, s) for r, s in product(self._ranks, self._suits)]


class Hand():

    def __init__(self, cards: list[Card], bet: int):
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
    def ranks(self):
        return [card.rank for card in self.cards]
    
    def add_card(self, card: Card):
        self.cards.append(card)
        self._check_hand()

    def double(self):
        self.bet *= 2

    def split(self, bet: int) -> Hand:
        other_hand = self.cards[1:]
        self.cards = self.cards[:1]
        return Hand(cards=other_hand, bet=bet)
    
    def min_total(self):
        return sum(1 if r == 'A' \
                   else 10 if r in {'J', 'Q', 'K'} \
                   else int(r) for r in self.ranks)
    
    def max_total(self):
        if 'A' in self.ranks:
            return self.min_total() + 10
        return self.min_total()
    
    def best_value(self):
        hand_max = self.max_total()
        if hand_max <= 21:
            return hand_max
        return self.min_total()

    def close(self):
        self.closed = True
    
    def surrender(self):
        self.closed = True
        self.surrendered = True
    
    def set_as_blackjack(self):
        self.blackjack = True


def play(start_money: int = 500,
         num_decks: int = 1,
         max_num_hands: int = 1,
         hit_soft_17: bool = False,
         double_after_splits: bool = False,
         split_in_aces: bool = False,
         restrict_double: bool = False,
         enable_surrender: bool = False,
         enable_hole_card: bool = False):
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
                          'Hit, stand, double, split, or surrender?' %i
                while True:
                    table_screen(dealer_hand=dealer_hand,
                                 hole_card=enable_hole_card,
                                 player_hands=player_hands,
                                 decisions=decisions,
                                 bankroll=bankroll,
                                 message=message)
                    decision = input('Your decision for HAND %d: ' %i)
                    if decision in {'hit', 'stand'}:
                        pass
                    elif decision == 'split':
                        if not num_split:
                            message = 'Cannot split HAND %d. ' \
                                      'Max number of hands reached.' %i
                            continue
                        if not split_in_aces and hand.ranks == ['A', 'A']:
                            message = 'Cannot split HAND %d. ' \
                                      'Split aces is not allowed.' %i
                            continue
                        if len(hand.cards) != 2 or len(set(hand.ranks)) != 1:
                            message = 'Cannot split HAND %d.' %i
                            continue
                        if hand.bet > temp_bankroll:
                            message = 'Cannot split HAND %d. ' \
                                      'You do not have enough funds.' %i
                            continue
                        temp_bankroll -= hand.bet
                    elif decision == 'double':
                        if len(player_hands) > 1 and not double_after_splits:
                            message = 'Cannot double HAND %d. ' \
                                      'Double after split is not allowed.' %i
                            continue
                        if restrict_double \
                                and hand.min_total() not in {9, 10, 11}:
                            message = 'Cannot double HAND %d. ' \
                                      'Double only allowed on 9, 10, or 11.' %i
                            continue
                        if hand.bet > temp_bankroll:
                            message = 'Cannot double HAND %d. ' \
                                      'You do not have enough funds.' %i
                            continue
                        temp_bankroll -= hand.bet
                    elif decision == 'surrender':
                        if not enable_surrender:
                            message = 'Invalid decision for HAND %d. ' \
                                      'Surrender is not allowed.' %i
                            continue
                        pass
                    else:
                        message = 'Not understood. ' \
                                  'Waiting decision for HAND %d.\n' \
                                  'Hit, stand, double, split, or surrender?' %i
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

def card_repr(card: Card):
    return '%s%s' %(card.rank, card.suit)

def ask_bet():
    response = input('Initial bet: $')
    try:
        return int(response)
    except ValueError:
        return None

def process_decisions(
        hands: list[Hand],
        decisions: list[Literal['hit', 'stand', 'double', 'split', 'surrender']],
        pile: DrawPile):
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
    if sorted(hand.ranks) == ['6', 'A']:
        if hit_soft_17:
            hand.add_card(pile.draw()[0])
        return
    while hand.min_total() < 17 and not hand.closed:
        hand.add_card(pile.draw()[0])

def get_results(dealer_hand: Hand, player_hands: list[Hand]):
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
    input('Press Enter to continue...')
    return

def end_of_game():
    clear_terminal()
    print('Sheesh! You lost all your money...')
    return enter_to_continue()

def terminate():
    """Script exit screen."""
    clear_terminal()
    print('Tranks for playing! Goodbye!')
    print('More in github.com/nelioasousa/python-study')

def clear_terminal():
    """Clear the terminal."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def menu(info: Union[str, None] = None):
    """Handle the menu screen."""
    clear_terminal()
    print('♣♥♠♦ BLACKJACK GAME ♣♥♠♦', end='\n\n')
    print('[P] PLAY\n[E] EXIT', end='\n\n')
    return input('Select: ').strip().lower()


def load_configs():
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

def reset_configs():
    configs = get_default_configs()
    save_configs(configs)
    return configs

def get_default_configs():
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
    from json import dump
    with open('./cfg.json', mode='w') as cfg_file:
        dump(configs, cfg_file, ensure_ascii=True, indent=4)

def handle_configs_error(error_message: str):
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
